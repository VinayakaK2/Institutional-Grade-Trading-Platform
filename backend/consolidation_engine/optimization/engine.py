import asyncio
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

from backend.consolidation_engine.optimization.models import (
    ConsolidationProcessingRequest,
    ConsolidationProcessingResult,
    ConsolidationOptimizationSnapshot,
    OptimizationBusinessStatistics,
    OptimizationRuntimeStatistics
)
from backend.consolidation_engine.optimization.contracts import (
    IConsolidationProcessor,
    IConsolidationOptimizationRepository
)
from backend.consolidation_engine.optimization.config import ConsolidationOptimizationConfiguration

logger = logging.getLogger(__name__)


class ConsolidationOptimizationEngine:
    """
    Optimization Facade enforcing incremental and parallel processing.
    Delegates strictly to domain-aware IConsolidationProcessor.
    """
    
    def __init__(
        self, 
        repository: IConsolidationOptimizationRepository,
        processor: IConsolidationProcessor,
        configuration: ConsolidationOptimizationConfiguration,
        optimization_algorithm_version: str = "1.0"
    ):
        self.repository = repository
        self.processor = processor
        self.configuration = configuration
        self.optimization_algorithm_version = optimization_algorithm_version

    async def _process_miss(
        self, 
        request: ConsolidationProcessingRequest, 
        semaphore: asyncio.Semaphore
    ) -> ConsolidationProcessingResult:
        """Worker function for executing a single cache-miss request concurrently."""
        async with semaphore:
            # Delegate to domain processor
            result = await self.processor.process(request)
            
            # Save the new result to the cache
            await self.repository.save_cached_result(result)
            return result

    async def process_batch(
        self, 
        requests: List[ConsolidationProcessingRequest],
        parent_snapshot_id: Optional[str] = None
    ) -> Tuple[List[ConsolidationProcessingResult], ConsolidationOptimizationSnapshot]:
        """
        Executes a batch of requests.
        Returns:
            - A list of ConsolidationProcessingResult in EXACTLY the same order as the input requests.
            - A ConsolidationOptimizationSnapshot detailing the run.
        """
        start_time = time.perf_counter()
        
        # We need to maintain original order. Keep track using request_id or index.
        # We'll map index -> Result.
        results_map: Dict[int, ConsolidationProcessingResult] = {}
        
        cache_hits = 0
        cache_misses = 0
        
        tasks_to_run = []
        
        # 1. Incremental Check
        for idx, req in enumerate(requests):
            fingerprint_str = req.fingerprint.digest
            
            cached = await self.repository.get_cached_result(fingerprint_str)
            if cached:
                cache_hits += 1
                # Mark as cached for this run
                cached_run = cached.model_copy(update={"cached": True})
                results_map[idx] = cached_run
            else:
                cache_misses += 1
                tasks_to_run.append((idx, req))
                
        # 2. Parallel Processing for Misses
        if tasks_to_run:
            semaphore = asyncio.Semaphore(self.configuration.max_concurrency)
            # Create gather tasks
            aws = [self._process_miss(req, semaphore) for _, req in tasks_to_run]
            computed_results = await asyncio.gather(*aws)
            
            # 3. Ordered Merge
            for (idx, _), res in zip(tasks_to_run, computed_results):
                results_map[idx] = res
                
        # Construct final ordered list
        final_results = [results_map[i] for i in range(len(requests))]
        
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000.0
        
        # 4. Generate Snapshot
        biz_stats = OptimizationBusinessStatistics(
            total_candidates=len(requests),
            cache_hits=cache_hits,
            cache_misses=cache_misses
        )
        
        runtime_stats = OptimizationRuntimeStatistics(
            execution_time_ms=execution_time_ms,
            batch_count=1, # single batch processed here
            worker_count=self.configuration.max_concurrency
        )
        
        timestamp = datetime.now(timezone.utc)
        
        # We just hash the config and stats together for a dummy snapshot fingerprint to trace execution
        payload = f"{parent_snapshot_id}_{cache_hits}_{cache_misses}_{execution_time_ms}"
        overall_fingerprint = payload
        
        snapshot = ConsolidationOptimizationSnapshot(
            snapshot_id=ConsolidationOptimizationSnapshot.generate_id(overall_fingerprint, timestamp),
            parent_snapshot_id=parent_snapshot_id,
            business_fingerprint=overall_fingerprint,
            fingerprint_version=self.configuration.fingerprint_version,
            optimization_algorithm_version=self.optimization_algorithm_version,
            business_statistics=biz_stats,
            runtime_statistics=runtime_stats,
            configuration_version=self.configuration.config_version,
            generated_timestamp=timestamp
        )
        
        await self.repository.save(snapshot)
        
        return final_results, snapshot
