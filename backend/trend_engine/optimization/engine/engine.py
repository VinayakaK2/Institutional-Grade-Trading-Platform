import time
from typing import List, Dict
import logging

from backend.trend_engine.optimization.contracts.contracts import (
    ITrendOptimizationEngine,
    ITrendOptimizationSnapshotRepository,
    ISymbolTrendCache,
    IParallelExecutor
)
from backend.trend_engine.optimization.models.models import (
    BusinessFingerprint,
    TrendOptimizationSnapshot,
    TrendOptimizationMetrics,
    SymbolPipelineResult
)
from backend.trend_engine.optimization.config.config import TrendOptimizationConfig
from backend.trend_engine.optimization.engine.incremental import IncrementalProcessor

# Assume these exist from previous phases
from backend.trend_engine.models.models import TrendSymbol, TrendSnapshot
from backend.trend_engine.quality.models.models import TrendQualitySnapshot, TrendQualitySymbolResult, TrendQualityMetadata
from backend.trend_engine.lifecycle.models.models import TrendLifecycleSnapshot, TrendLifecycleSymbolResult

from backend.trend_engine.contracts.contracts import ITrendEngine, ITrendRepository
from backend.trend_engine.quality.contracts.contracts import ITrendQualityEngine, ITrendQualityRepository
from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleEngine, ITrendLifecycleRepository

logger = logging.getLogger(__name__)

class TrendOptimizationEngine(ITrendOptimizationEngine):
    """
    Core Optimization Orchestrator.
    Executes Detection -> Quality -> Lifecycle pipeline using incremental caching
    and deterministic parallel batching.
    """
    def __init__(
        self,
        config: TrendOptimizationConfig,
        detection_engine: ITrendEngine,
        detection_repo: ITrendRepository,
        quality_engine: ITrendQualityEngine,
        quality_repo: ITrendQualityRepository,
        lifecycle_engine: ITrendLifecycleEngine,
        lifecycle_repo: ITrendLifecycleRepository,
        snapshot_repo: ITrendOptimizationSnapshotRepository,
        symbol_cache: ISymbolTrendCache,
        parallel_executor: IParallelExecutor
    ):
        self._config = config
        self._detection_engine = detection_engine
        self._detection_repo = detection_repo
        self._quality_engine = quality_engine
        self._quality_repo = quality_repo
        self._lifecycle_engine = lifecycle_engine
        self._lifecycle_repo = lifecycle_repo
        self._snapshot_repo = snapshot_repo
        self._symbol_cache = symbol_cache
        self._parallel_executor = parallel_executor
        
        self._incremental_processor = IncrementalProcessor(symbol_cache)

    async def run_optimized_pipeline(
        self,
        symbols: List[TrendSymbol],
        business_fingerprint: BusinessFingerprint,
        source_watchlist_snapshot_id: str,
        source_watchlist_version: int,
        source_indicator_snapshot_id: str,
        source_indicator_snapshot_version: int,
        source_structure_snapshot_id: str,
        source_structure_snapshot_version: int,
    ) -> TrendOptimizationSnapshot:
        
        start_time = time.time()
        
        fingerprint_hash = business_fingerprint.compute_hash()
        
        symbols_to_process: List[TrendSymbol] = []
        symbols_reused: Dict[str, SymbolPipelineResult] = {}
        
        def get_sym_key(s):
            # Optimization layer helper. 
            # In production, s is expected to be a fully valid TrendSymbol.
            # We fallback to symbol_key ONLY for mock objects during testing.
            if hasattr(s, "watchlist_symbol") and getattr(s, "watchlist_symbol", None) is not None:
                return f"{s.watchlist_symbol.symbol.symbol}:{s.watchlist_symbol.symbol.exchange.code}"
            
            # Fallback for testing/mocks
            if hasattr(s, "symbol_key"):
                return getattr(s, "symbol_key")
                
            raise ValueError("Invalid symbol object passed to optimization engine. Missing watchlist_symbol.")
            
        if self._config.is_incremental_enabled and self._config.is_cache_enabled:
            # Check cache
            keys = [get_sym_key(s) for s in symbols]
            miss_keys, reused = await self._incremental_processor.filter_candidates(fingerprint_hash, keys)
            
            # Filter the actual models for misses
            miss_set = set(miss_keys)
            symbols_to_process = [s for s in symbols if get_sym_key(s) in miss_set]
            symbols_reused = reused
        else:
            symbols_to_process = symbols
            
        # Execute missing symbols in chunks
        chunked_results: List[SymbolPipelineResult] = []
        parallel_time_ms = 0.0
        
        if symbols_to_process:
            # define chunking logic
            batch_size = self._config.batch_size
            chunks = [symbols_to_process[i:i+batch_size] for i in range(0, len(symbols_to_process), batch_size)]
            
            async def process_chunk(chunk: List[TrendSymbol]) -> List[SymbolPipelineResult]:
                # 1. Detection
                d_snap = await self._detection_engine.generate_trend_snapshot(
                    symbols=chunk,
                    source_watchlist_snapshot_id=source_watchlist_snapshot_id,
                    source_watchlist_version=source_watchlist_version,
                    source_indicator_snapshot_id=source_indicator_snapshot_id,
                    source_indicator_snapshot_version=source_indicator_snapshot_version,
                    source_structure_snapshot_id=source_structure_snapshot_id,
                    source_structure_snapshot_version=source_structure_snapshot_version
                )
                
                # 2. Quality
                q_snap = await self._quality_engine.evaluate_trend_quality(d_snap)
                
                # 3. Lifecycle
                l_snap = await self._lifecycle_engine.evaluate_lifecycle(d_snap, q_snap)
                
                # Helper to extract symbol key safely depending on TrendSymbol structure
                def get_key(s):
                    return f"{s.watchlist_symbol.symbol.symbol}:{s.watchlist_symbol.symbol.exchange.code}" if hasattr(s, "watchlist_symbol") else getattr(s, "symbol_key", "UNKNOWN")
                
                d_snap_dict = {get_key(s): s for s in d_snap.symbols}
                q_snap_dict = {s.symbol_key: s for s in q_snap.symbols}
                
                results = []
                for sym in chunk:
                    k = get_key(sym)
                    res = SymbolPipelineResult(
                        symbol_key=k,
                        detection_result=d_snap_dict[k].model_dump(),
                        quality_result=q_snap_dict[k].model_dump(),
                        lifecycle_result=l_snap.symbols[k].model_dump()
                    )
                    results.append(res)
                return results

            p_start = time.time()
            if self._config.is_parallel_enabled:
                # Parallel execution guarantees order of chunks
                nested_results = await self._parallel_executor.execute_in_parallel(
                    items=chunks,
                    task_func=process_chunk,
                    worker_count=self._config.worker_count,
                    batch_size=self._config.batch_size
                )
                # Flatten
                for res_list in nested_results:
                    chunked_results.extend(res_list)
            else:
                # Sequential execution
                for chunk in chunks:
                    chunked_results.extend(await process_chunk(chunk))
            
            parallel_time_ms = (time.time() - p_start) * 1000.0

            # Save newly computed to cache
            if self._config.is_cache_enabled:
                for res in chunked_results:
                    await self._symbol_cache.save_cached_result(fingerprint_hash, res)
                    
        # Ordered Merge: Combine reused and newly processed in original input order
        final_results: List[SymbolPipelineResult] = []
        chunked_dict = {res.symbol_key: res for res in chunked_results}
        
        for sym in symbols:
            k = get_sym_key(sym)
            if k in symbols_reused:
                final_results.append(symbols_reused[k])
            elif k in chunked_dict:
                final_results.append(chunked_dict[k])
            else:
                raise RuntimeError(f"Missing result for symbol {k} during merge.")

        # Construct Business Snapshots
        d_symbols = [TrendSymbol(**r.detection_result) for r in final_results]
        q_symbols = [TrendQualitySymbolResult(**r.quality_result) for r in final_results]
        l_symbols = {r.symbol_key: TrendLifecycleSymbolResult(**r.lifecycle_result) for r in final_results}
        
        # We need a new snapshot ID for these. We'll generate a dummy ID for now or use timestamp
        import uuid
        base_id = str(uuid.uuid4())
        
        from datetime import datetime, timezone
        
        final_d_snap = TrendSnapshot(
            snapshot_id=f"d_{base_id}",
            snapshot_version=1,
            created_at=datetime.now(timezone.utc),
            source_watchlist_snapshot_id=source_watchlist_snapshot_id,
            source_watchlist_version=source_watchlist_version,
            source_indicator_snapshot_id=source_indicator_snapshot_id,
            source_indicator_snapshot_version=source_indicator_snapshot_version,
            source_structure_snapshot_id=source_structure_snapshot_id,
            source_structure_snapshot_version=source_structure_snapshot_version,
            symbols=d_symbols,
            pipeline_version=business_fingerprint.detection_algorithm_version,
            configuration_hash=business_fingerprint.detection_config_hash,
            schema_version="1.0",
            execution_metadata={},
            audit_metadata={}
        )
        
        final_q_snap = TrendQualitySnapshot(
            quality_snapshot_id=f"q_{base_id}",
            source_trend_snapshot_id=final_d_snap.snapshot_id,
            symbols=q_symbols,
            metadata=TrendQualityMetadata(
                pipeline_version=business_fingerprint.quality_algorithm_version,
                configuration_hash=business_fingerprint.quality_config_hash,
                configuration_version=1,
                quality_algorithm_version=business_fingerprint.quality_algorithm_version,
                evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
                evaluation_duration_ms=0.0
            )
        )
        
        final_l_snap = TrendLifecycleSnapshot(
            snapshot_id=f"l_{base_id}",
            snapshot_version=1,
            parent_trend_snapshot_id=final_d_snap.snapshot_id,
            parent_trend_quality_snapshot_id=final_q_snap.quality_snapshot_id,
            symbols=l_symbols,
            pipeline_version=business_fingerprint.lifecycle_algorithm_version,
            configuration_hash=business_fingerprint.lifecycle_config_hash,
            lifecycle_algorithm_version=business_fingerprint.lifecycle_algorithm_version,
            lifecycle_rule_version=business_fingerprint.lifecycle_rule_version
        )

        # Save Business Snapshots
        await self._detection_repo.save_snapshot(final_d_snap)
        await self._quality_repo.save_quality_snapshot(final_q_snap)
        await self._lifecycle_repo.save_lifecycle_snapshot(final_l_snap)

        # Construct Optimization Snapshot
        exec_duration_ms = (time.time() - start_time) * 1000.0
        metrics = TrendOptimizationMetrics(
            symbols_processed_total=len(symbols),
            symbols_reused_from_cache=len(symbols_reused),
            symbols_recomputed=len(symbols_to_process),
            cache_hit_rate_percentage=(len(symbols_reused) / len(symbols) * 100.0) if symbols else 0.0,
            execution_duration_ms=exec_duration_ms,
            parallel_execution_time_ms=parallel_time_ms
        )

        final_opt_snap = TrendOptimizationSnapshot(
            snapshot_id=f"opt_{base_id}",
            snapshot_version=1,
            trend_snapshot_id=final_d_snap.snapshot_id,
            trend_quality_snapshot_id=final_q_snap.quality_snapshot_id,
            trend_lifecycle_snapshot_id=final_l_snap.snapshot_id,
            business_fingerprint=business_fingerprint,
            fingerprint_hash=fingerprint_hash,
            configuration_hash=self._config.configuration_hash,
            metrics=metrics
        )
        
        await self._snapshot_repo.save_snapshot(final_opt_snap)
        
        return final_opt_snap
