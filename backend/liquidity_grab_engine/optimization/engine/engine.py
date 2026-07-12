import time
import hashlib
import logging
from typing import List, Tuple, Dict

from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot
from backend.liquidity_grab_engine.lifecycle.engine.engine import LiquidityGrabLifecycleEngine
from backend.liquidity_grab_engine.optimization.models.models import (
    OptimizationContext,
    BusinessFingerprint,
    OptimizationRuntimeStatistics,
    OptimizationMetadata,
    OptimizationSnapshot
)
from backend.liquidity_grab_engine.optimization.contracts.repository import IOptimizationRepository
from backend.liquidity_grab_engine.optimization.execution.batch import AsyncBatchExecutor

logger = logging.getLogger(__name__)

class LiquidityGrabOptimizationEngine:
    """
    Wraps the LiquidityGrabLifecycleEngine to provide incremental execution,
    caching, and deterministic parallelization.
    """
    
    def __init__(
        self,
        lifecycle_engine: LiquidityGrabLifecycleEngine,
        repository: IOptimizationRepository,
        engine_version: str = "1.0.0"
    ) -> None:
        self._lifecycle_engine = lifecycle_engine
        self._repository = repository
        self._engine_version = engine_version

    def _generate_fingerprint(self, context: LiquidityGrabLifecycleContext) -> BusinessFingerprint:
        # Generate fingerprint components deterministically
        return BusinessFingerprint(
            candidate_id=context.candidate.candidate_id,
            dataset_version=context.candidate.dataset_version,
            config_hash=context.candidate.configuration_hash,
            detection_algorithm_version=context.candidate.metadata.pipeline_version,
            quality_algorithm_version=context.quality_report.metadata.pipeline_version,
            lifecycle_algorithm_version=context.lifecycle_summary.aggregator_version if hasattr(context, 'lifecycle_summary') else "1.0.0"
        )
        
    def _create_snapshot(self, 
                         lifecycle_snapshot: LiquidityGrabLifecycleSnapshot, 
                         fingerprint: BusinessFingerprint,
                         stats: OptimizationRuntimeStatistics) -> OptimizationSnapshot:
        meta = OptimizationMetadata(
            optimization_engine_version=self._engine_version,
            optimization_timestamp=time.time()
        )
        snapshot_payload = f"{lifecycle_snapshot.snapshot_id}_{fingerprint.fingerprint_hash}_{meta.optimization_engine_version}"
        snapshot_id = hashlib.sha256(snapshot_payload.encode("utf-8")).hexdigest()
        
        return OptimizationSnapshot(
            snapshot_id=snapshot_id,
            business_fingerprint=fingerprint,
            lifecycle_snapshot=lifecycle_snapshot,
            metadata=meta,
            runtime_statistics=stats
        )

    async def execute_batch(
        self, 
        contexts: List[LiquidityGrabLifecycleContext], 
        opt_context: OptimizationContext
    ) -> List[OptimizationSnapshot]:
        
        start_time = time.time()
        logger.info(f"Starting optimization run for {len(contexts)} candidates")
        
        fingerprints: List[BusinessFingerprint] = []
        cached_results: Dict[str, OptimizationSnapshot] = {}
        to_execute: List[Tuple[int, LiquidityGrabLifecycleContext, BusinessFingerprint]] = []
        
        # Step 1: Fingerprint Generation & Cache Interrogation
        for idx, ctx in enumerate(contexts):
            fingerprint = self._generate_fingerprint(ctx)
            fingerprints.append(fingerprint)
            
            fingerprint_hash = fingerprint.fingerprint_hash
            
            if opt_context.cache_enabled and opt_context.reuse_enabled:
                cached_snapshot = await self._repository.load(fingerprint_hash)
                if cached_snapshot:
                    cached_results[fingerprint_hash] = cached_snapshot
                    continue
            
            to_execute.append((idx, ctx, fingerprint))
            
        cache_hits = len(cached_results)
        cache_misses = len(to_execute)
        
        # Step 2: Parallel Batch Execution for Misses
        batch_count = 0
        new_snapshots_dict: Dict[int, OptimizationSnapshot] = {}
        
        if to_execute:
            executor = AsyncBatchExecutor(
                batch_size=opt_context.batch_size, 
                max_parallelism=opt_context.max_parallelism
            )
            
            contexts_to_execute = [tup[1] for tup in to_execute]
            batch_count = (len(contexts_to_execute) + opt_context.batch_size - 1) // opt_context.batch_size
            
            logger.info(f"Executing {cache_misses} candidates in {batch_count} batches")
            
            # Execute all
            lifecycle_snapshots = await executor.execute_batch(
                items=contexts_to_execute,
                task_func=self._lifecycle_engine.execute
            )
            
            # Package them into OptimizationSnapshots
            for i, lifecycle_snap in enumerate(lifecycle_snapshots):
                original_idx = to_execute[i][0]
                fingerprint = to_execute[i][2]
                
                temp_stats = OptimizationRuntimeStatistics(
                    candidates_processed=len(contexts),
                    candidates_reused=cache_hits,
                    cache_hits=cache_hits,
                    cache_misses=cache_misses,
                    batch_count=batch_count,
                    execution_duration_ms=0.0 # Will finalize later
                )
                
                opt_snap = self._create_snapshot(lifecycle_snap, fingerprint, temp_stats)
                new_snapshots_dict[original_idx] = opt_snap
                
                if opt_context.cache_enabled:
                    await self._repository.save(opt_snap)

        # Step 3: Result Merging & Deterministic Output Ordering
        final_snapshots: List[OptimizationSnapshot] = []
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000.0
        
        final_stats = OptimizationRuntimeStatistics(
            candidates_processed=len(contexts),
            candidates_reused=cache_hits,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            batch_count=batch_count,
            execution_duration_ms=duration_ms
        )

        for i, fingerprint in enumerate(fingerprints):
            if i in new_snapshots_dict:
                # Update stats on newly computed
                old_snap = new_snapshots_dict[i]
                final_snap = old_snap.model_copy(update={'runtime_statistics': final_stats})
                final_snapshots.append(final_snap)
            else:
                # Retrieve from cache
                cached_snap = cached_results[fingerprint.fingerprint_hash]
                # We could update the runtime stats on the cached copy for the current run perspective, 
                # but typically cache objects shouldn't mutate. Since snapshots are immutable, we 
                # duplicate them with updated run stats so the caller sees the current run's stats.
                final_snap = cached_snap.model_copy(update={'runtime_statistics': final_stats})
                final_snapshots.append(final_snap)

        logger.info(f"Optimization run completed. Hits: {cache_hits}, Misses: {cache_misses}, Duration: {duration_ms:.2f}ms")
        return final_snapshots
