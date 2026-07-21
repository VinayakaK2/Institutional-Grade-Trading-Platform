from typing import List, Any
import time
from backend.risk_optimization_engine.models.request import OptimizationRequest
from backend.risk_optimization_engine.contracts.cache import ICacheStore
from backend.risk_optimization_engine.contracts.pipeline import IRiskPipeline
from backend.risk_optimization_engine.core.statistics import StatisticsCollector
from backend.risk_optimization_engine.core.executor import AsyncBatchExecutor
from backend.risk_optimization_engine.core.generator import FingerprintGenerator

class RiskOptimizationEngine:
    """
    Wraps the underlying risk pipeline to provide incremental execution,
    caching, parallel processing, and ordered merge.
    """
    def __init__(
        self,
        cache: ICacheStore,
        pipeline: IRiskPipeline,
        statistics: StatisticsCollector,
        executor: AsyncBatchExecutor
    ):
        self._cache = cache
        self._pipeline = pipeline
        self._statistics = statistics
        self._executor = executor
        
    async def execute_batch(self, requests: List[OptimizationRequest]) -> List[Any]:
        """
        Executes a batch of optimization requests.
        """
        start_time = time.perf_counter()
        
        cache_hits = 0
        cache_misses = 0
        
        # Determine cache hits vs misses
        # We need to maintain the original order
        results: List[Any] = [None] * len(requests)
        miss_indices: List[int] = []
        miss_requests: List[OptimizationRequest] = []
        
        for idx, request in enumerate(requests):
            cache_key = FingerprintGenerator.generate_cache_key(request)
            if await self._cache.exists(cache_key):
                cached_snapshot = await self._cache.load(cache_key)
                results[idx] = cached_snapshot
                cache_hits += 1
            else:
                miss_indices.append(idx)
                miss_requests.append(request)
                cache_misses += 1
                
        # Execute misses in parallel batches
        async def process_miss(request: OptimizationRequest) -> Any:
            snapshot = await self._pipeline.execute(request)
            cache_key = FingerprintGenerator.generate_cache_key(request)
            await self._cache.save(cache_key, snapshot)
            return snapshot
            
        if miss_requests:
            miss_results = await self._executor.execute_in_batches(miss_requests, process_miss)
            
            # Place results back in their original order
            for i, idx in enumerate(miss_indices):
                results[idx] = miss_results[i]
                
        processing_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Record statistics
        batch_count = (len(miss_requests) // self._executor._batch_size) + (1 if len(miss_requests) % self._executor._batch_size != 0 else 0)
        
        try:
            await self._statistics.record_batch(
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                total_snapshots=len(requests),
                processing_time_ms=processing_time_ms,
                parallelism=self._executor._max_workers > 1,
                worker_count=self._executor._max_workers,
                batch_count=batch_count
            )
        except Exception:
            # Metrics failure should never block business execution
            pass
        
        return results
