"""
Optimized Watchlist Execution Pipeline
======================================

Wraps an inner WatchlistExecutionPipeline to provide:
- Incremental reuse of unchanged candidates
- Parallel batch execution
- Context cloning for safe shared_state boundaries
"""
import asyncio
import time
from typing import List, Optional, Tuple, Any

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistPipeline, IWatchlistStage, IWatchlistRepository
from backend.watchlist_engine.models.models import (
    WatchlistExecutionContext,
    WatchlistCandidate,
    WatchlistSnapshot,
)
from backend.watchlist_engine.models.config import WatchlistOptimizationSettings
from backend.watchlist_engine.optimization.fingerprint import OptimizationFingerprintBuilder

logger = get_logger(__name__)


class OptimizedWatchlistPipeline(IWatchlistPipeline):
    """
    Decorator for IWatchlistPipeline that adds parallel batching and incremental processing.
    """

    def __init__(
        self, 
        inner: IWatchlistPipeline, 
        settings: WatchlistOptimizationSettings,
        repository: IWatchlistRepository
    ):
        self._inner = inner
        self._settings = settings
        self._repository = repository

    def register_stage(self, stage: IWatchlistStage) -> None:
        """Pass-through to inner pipeline."""
        self._inner.register_stage(stage)

    async def execute(self, context: WatchlistExecutionContext) -> WatchlistExecutionContext:
        """
        Executes the pipeline with optimizations.
        
        Steps:
        1. Change Detection: Identifies 'reused' vs 'processed' candidates.
        2. Batching: Splits 'processed' candidates into batches.
        3. Parallel Execution: Runs the inner pipeline on each batch safely.
        4. Snapshot Finalization: Merges results.
        """
        start_time = time.perf_counter()
        
        # 1. Change Detection & Incremental Builder
        reused_candidates, candidates_to_process = await self._detect_changes(context)
        
        processed_candidates_list: List[WatchlistCandidate] = []
        all_stage_results: List[Any] = []
        
        if not candidates_to_process:
            logger.info(f"All {len(reused_candidates)} candidates reused. Skipping processing.")
        else:
            # 2 & 3. Batching and Parallel Execution
            if self._settings.enable_parallel_execution:
                processed_candidates_list, all_stage_results = await self._execute_parallel(
                    context, candidates_to_process
                )
            else:
                processed_candidates_list, all_stage_results = await self._execute_sequential(
                    context, candidates_to_process
                )

        # 4. Snapshot Finalization
        # Merge candidates
        final_candidates = reused_candidates + processed_candidates_list
        context.candidates = final_candidates
        
        # Record reuse statistics in context metadata FIRST so merge can use it
        context.metadata["optimization_stats"] = {
            "total_candidates": len(final_candidates),
            "processed_candidates": len(candidates_to_process),
            "reused_candidates": len(reused_candidates),
            "reuse_percentage": (len(reused_candidates) / len(final_candidates)) * 100 if final_candidates else 0.0,
            "incremental_enabled": self._settings.enable_incremental_processing,
            "parallel_enabled": self._settings.enable_parallel_execution,
            "worker_count": self._settings.max_parallel_workers if self._settings.enable_parallel_execution else 1,
            "batch_size": self._settings.batch_size,
            "execution_time_ms": (time.perf_counter() - start_time) * 1000,
            "fingerprint_version": OptimizationFingerprintBuilder.FINGERPRINT_VERSION
        }
        
        
        # Calculate and store the fingerprint for future optimization bypasses
        fingerprint = OptimizationFingerprintBuilder.build(
            dataset_version="n/a", 
            config_hash=context.metadata.get("config_hash", "unknown"),
            candidates=context.candidates
        )
        context.metadata["optimization_fingerprint"] = fingerprint
        
        # Merge stage results (from processed candidates only)
        # To avoid duplicating results, we just append the batch results or sequential results.
        # Since the inner pipeline tracks stage execution times, parallel batches will produce 
        # multiple sets of stage results. We aggregate them by keeping the first batch's stage names
        # and summing the durations, or we just append them all.
        self._merge_stage_results(context, all_stage_results)

        return context

    async def _detect_changes(self, context: WatchlistExecutionContext) -> Tuple[List[WatchlistCandidate], List[WatchlistCandidate]]:
        """
        Splits candidates into those that can be reused and those that must be processed.
        """
        if not self._settings.enable_incremental_processing:
            return [], context.candidates
            
        previous_snapshot: Optional[WatchlistSnapshot] = await self._repository.load_latest_snapshot()
        config_hash = context.metadata.get("config_hash")
        
        if not previous_snapshot:
            return [], context.candidates
            
        prev_config_hash = previous_snapshot.config_hash
        
        # Incremental reuse is ONLY safe if config is identical.
        if config_hash != prev_config_hash:
            logger.info("Config changed. Forcing full recalculation.")
            return [], context.candidates
            
        # Build map of previous candidates
        prev_map = {
            f"{c.watchlist_symbol.symbol.symbol}:{c.watchlist_symbol.symbol.exchange.code}": c
            for c in previous_snapshot.candidates
        }
        
        reused = []
        to_process = []
        
        for candidate in context.candidates:
            key = f"{candidate.watchlist_symbol.symbol.symbol}:{candidate.watchlist_symbol.symbol.exchange.code}"
            if key in prev_map:
                # Reuse the historically processed candidate entirely
                reused.append(prev_map[key])
            else:
                to_process.append(candidate)
                
        return reused, to_process

    async def _execute_parallel(
        self, context: WatchlistExecutionContext, candidates: List[WatchlistCandidate]
    ) -> Tuple[List[WatchlistCandidate], List[Any]]:
        
        batch_size = self._settings.batch_size
        batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]
        
        semaphore = asyncio.Semaphore(self._settings.max_parallel_workers)
        
        async def process_batch(batch: List[WatchlistCandidate]):
            async with semaphore:
                # Context Splitting: shared_state is READ-ONLY. We pass a shallow copy of shared_state
                # and stage_results to isolate batch execution.
                batch_context = WatchlistExecutionContext(
                    run_id=context.run_id,
                    snapshot_id=context.snapshot_id,
                    started_at=context.started_at,
                    candidates=batch,
                    shared_state=context.shared_state.copy(), # shallow copy, treated as read-only by stages
                    metadata=context.metadata.copy(),
                    stage_results=[]
                )
                
                # Execute inner pipeline on the batch
                result_context = await self._inner.execute(batch_context)
                return result_context.candidates, result_context.stage_results

        tasks = [process_batch(b) for b in batches]
        results = await asyncio.gather(*tasks)
        
        final_candidates = []
        all_stage_results = []
        for batch_candidates, batch_stage_results in results:
            final_candidates.extend(batch_candidates)
            all_stage_results.append(batch_stage_results)
            
        return final_candidates, all_stage_results

    async def _execute_sequential(
        self, context: WatchlistExecutionContext, candidates: List[WatchlistCandidate]
    ) -> Tuple[List[WatchlistCandidate], List[Any]]:
        
        seq_context = WatchlistExecutionContext(
            run_id=context.run_id,
            snapshot_id=context.snapshot_id,
            started_at=context.started_at,
            candidates=candidates,
            shared_state=context.shared_state.copy(),
            metadata=context.metadata.copy(),
            stage_results=[]
        )
        
        result_context = await self._inner.execute(seq_context)
        return result_context.candidates, [result_context.stage_results]

    def _merge_stage_results(self, context: WatchlistExecutionContext, all_batch_results: List[List[Any]]) -> None:
        """
        Merges stage results from multiple batches into the main context.
        We aggregate duration times across batches so the final snapshot accurately reflects
        the total CPU time spent in each stage.
        """
        if not all_batch_results:
            return
            
        # Use the structure of the first batch's results
        base_results = all_batch_results[0]
        
        # We always want to aggregate and add optimization metadata
        # even if there's only 1 batch.
        
        from backend.watchlist_engine.models.models import WatchlistStageResult, WatchlistStageStatus
        
        aggregated_results = []
        
        for i, base_stage in enumerate(base_results):
            total_duration = 0.0
            overall_status = base_stage.status
            all_warnings = list(base_stage.warnings)
            
            for batch_res in all_batch_results:
                if i < len(batch_res):
                    b_stage = batch_res[i]
                    total_duration += b_stage.duration_ms
                    all_warnings.extend(b_stage.warnings)
                    if b_stage.status == WatchlistStageStatus.FAILED:
                        overall_status = WatchlistStageStatus.FAILED
            
            reused_cands = context.metadata.get("optimization_stats", {}).get("reused_candidates", 0)
            agg_metadata = dict(base_stage.metadata)
            agg_metadata["optimization"] = {
                "processed_candidates": len(context.candidates) - reused_cands,
                "reused_candidates": reused_cands
            }
            
            agg = WatchlistStageResult(
                stage_name=base_stage.stage_name,
                status=overall_status,
                duration_ms=total_duration,
                metadata=agg_metadata,
                warnings=all_warnings
            )
            aggregated_results.append(agg)
            
        context.stage_results = aggregated_results
