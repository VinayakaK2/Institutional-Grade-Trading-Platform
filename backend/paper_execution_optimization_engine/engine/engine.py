import hashlib
import time
from typing import List, Tuple
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot, OptimizationRuntimeStatistics
from backend.paper_execution_optimization_engine.contracts.cache import ICacheStore
from backend.paper_execution_optimization_engine.contracts.repository import IPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.executor.async_batch_executor import ExecutionExecutor
from backend.paper_execution_optimization_engine.engine.execution_reuse_planner import ExecutionReusePlanner
from backend.paper_execution_optimization_engine.config.config import OPTIMIZATION_ENGINE_VERSION
from backend.paper_execution_optimization_engine.repository.memory_repo import OptimizationRepositoryIntegrityError, OptimizationRepositoryCorruptionError
from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.contracts.repository import PaperExecutionResultRepository


class PaperExecutionOptimizationEngine:
    """
    Main orchestration wrapper pulling together the Reuse Planner, Cache, 
    Executor, and Snapshots into one continuous optimization pipeline.
    """
    def __init__(
        self,
        result_engine: PaperExecutionResultEngine,
        business_repository: PaperExecutionResultRepository,
        executor: ExecutionExecutor,
        cache: ICacheStore,
        repository: IPaperExecutionOptimizationRepository
    ):
        self._result_engine = result_engine
        self._business_repository = business_repository
        self._executor = executor
        self._cache = cache
        self._repository = repository

    async def execute_batch(
        self, 
        contexts: List[PaperExecutionOptimizationContext],
        current_dataset_version: str,
        current_pipeline_version: str,
        current_optimization_config_hash: str
    ) -> List[Tuple[PaperExecutionOptimizationSnapshot, PaperExecutionSnapshot]]:
        """
        Executes a batch of contexts deterministically, utilizing incremental caching.
        """
        import asyncio
        start_time = time.time()
        
        # 1. Reuse Planning
        planner = ExecutionReusePlanner(
            current_dataset_version,
            current_pipeline_version,
            current_optimization_config_hash
        )
        planned_batch = planner.plan_batch(contexts)
        
        cache_hits = 0
        cache_misses = 0
        reused_snapshots = 0
        recomputed_snapshots = 0
        
        final_results_unordered = []
        
        # We process each item. For misses, we aggregate them for parallel batch execution.
        misses_to_execute = []
        
        for idx, (ctx, fp, is_reusable) in enumerate(planned_batch):
            
            if is_reusable and ctx.optimization_configuration.caching_enabled:
                try:
                    # Attempt load from cache first instead of resolve, because we want to batch execute misses
                    opt_snap: PaperExecutionOptimizationSnapshot = await self._cache.load(fp)
                    if opt_snap.optimization_fingerprint == fp:
                        # Fingerprint verification passed
                        cache_hits += 1
                        reused_snapshots += 1
                        
                        # Load the business snapshot (sync)
                        biz_snap = await self._executor.execute_sync(
                            lambda: self._business_repository.load(opt_snap.snapshot_version)
                        )
                        final_results_unordered.append((idx, opt_snap, biz_snap))
                        continue
                except KeyError:
                    # Cache miss or not found
                    pass
            
            cache_misses += 1
            recomputed_snapshots += 1
            
            # Prepare task for batch execution
            # The task is a callable that returns the business snapshot
            def make_task(c=ctx):
                return lambda: self._result_engine.execute(c.execution_context)
                
            misses_to_execute.append((idx, ctx, fp, make_task()))

        # 2. Batch Execution
        if misses_to_execute:
            tasks = [t for _, _, _, t in misses_to_execute]
            batch_results = await self._executor.execute_batch(
                tasks,
                concurrency_limit=misses_to_execute[0][1].optimization_configuration.concurrency_limit,
                fail_fast=misses_to_execute[0][1].optimization_configuration.fail_fast
            )
            
            new_opt_snapshots = []
            
            # 3. Build Optimization Snapshots
            for (idx, ctx, fp, _), biz_snap in zip(misses_to_execute, batch_results):
                # Must persist business snapshot if not already done
                await self._executor.execute_sync(lambda: self._business_repository.save(biz_snap))
                
                # Canonical Hash payload
                payload = f"{fp}_{biz_snap.snapshot_version}_{OPTIMIZATION_ENGINE_VERSION}"
                canonical_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
                
                opt_snap = PaperExecutionOptimizationSnapshot(
                    optimization_fingerprint=fp,
                    business_fingerprint=biz_snap.business_fingerprint,
                    canonical_hash=canonical_hash,
                    snapshot_version=biz_snap.snapshot_version,
                    optimization_summary=OptimizationRuntimeStatistics(), # Filled later
                    metadata=ctx.optimization_metadata
                )
                
                new_opt_snapshots.append(opt_snap)
                final_results_unordered.append((idx, opt_snap, biz_snap))
                
                # Save to cache
                if ctx.optimization_configuration.caching_enabled:
                    await self._cache.save(opt_snap)
                    
            # Save optimization snapshots
            if new_opt_snapshots:
                try:
                    await self._repository.save_many(new_opt_snapshots)
                except OptimizationRepositoryIntegrityError:
                    # Fallback to saving individually and verifying
                    for snap in new_opt_snapshots:
                        try:
                            await self._repository.save(snap)
                        except OptimizationRepositoryIntegrityError as e:
                            existing = await self._repository.load(snap.optimization_fingerprint)
                            if existing.is_business_equivalent(snap):
                                pass # Safe duplicate (Concurrent Execution)
                            else:
                                raise OptimizationRepositoryCorruptionError(
                                    f"Fingerprint collision or cache corruption detected for {snap.optimization_fingerprint}"
                                ) from e
            
        # 4. Ordered Merge
        final_results_unordered.sort(key=lambda x: x[0])
        
        batch_duration_ms = (time.time() - start_time) * 1000.0
        avg_duration = batch_duration_ms / max(1, len(contexts))
        
        # We need to construct final stats. Since OptimizationRuntimeStatistics is frozen, 
        # we can just use a shared stats object for the caller to observe, or attach to return.
        # But opt_snap is frozen, so replacing stats on the fly requires object replacement.
        # For simplicity, we just return the pairs. The metrics are operational.
        
        final_output = []
        for idx, opt_snap, biz_snap in final_results_unordered:
            # We construct a new one with the final batch stats
            final_stats = OptimizationRuntimeStatistics(
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                reused_snapshots=reused_snapshots,
                recomputed_snapshots=recomputed_snapshots,
                parallel_workers=len(misses_to_execute) if misses_to_execute else 1,
                batch_duration_ms=batch_duration_ms,
                average_snapshot_duration_ms=avg_duration
            )
            # Recreate with final stats
            updated_opt_snap = PaperExecutionOptimizationSnapshot(
                optimization_fingerprint=opt_snap.optimization_fingerprint,
                business_fingerprint=opt_snap.business_fingerprint,
                canonical_hash=opt_snap.canonical_hash,
                snapshot_version=opt_snap.snapshot_version,
                optimization_summary=final_stats,
                metadata=opt_snap.metadata
            )
            final_output.append((updated_opt_snap, biz_snap))
            
        return final_output
