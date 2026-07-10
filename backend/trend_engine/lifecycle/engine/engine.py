import time
import hashlib
import json
from typing import List

from backend.trend_engine.lifecycle.contracts.contracts import (
    ITrendLifecycleEngine, 
    ITrendLifecycleStage, 
    ITrendLifecycleRepository
)
from backend.trend_engine.lifecycle.config.config import TrendLifecycleConfig
from backend.trend_engine.lifecycle.models.models import (
    TrendLifecycleSnapshot, 
    TrendLifecycleSymbolResult
)
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.pipeline.pipeline import TrendLifecyclePipeline
from backend.trend_engine.lifecycle.exceptions import LifecycleEvaluationError

from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.quality.models.models import TrendQualitySnapshot

class TrendLifecycleEngine(ITrendLifecycleEngine):
    """
    Main entry point for evaluating a Trend Lifecycle.
    """
    def __init__(
        self, 
        repository: ITrendLifecycleRepository, 
        config: TrendLifecycleConfig,
        stages: List[ITrendLifecycleStage]
    ):
        self._repository = repository
        self._config = config
        self._pipeline = TrendLifecyclePipeline(stages)

    async def evaluate_lifecycle(
        self, 
        trend_snapshot: TrendSnapshot, 
        quality_snapshot: TrendQualitySnapshot
    ) -> TrendLifecycleSnapshot:
        start_time = time.time()
        
        # 1. Pipeline Execution (starts with Validation)
        context = LifecycleExecutionContext(
            config=self._config,
            trend_snapshot=trend_snapshot,
            quality_snapshot=quality_snapshot
        )
        
        # Optionally retrieve previous state to track valid transitions.
        # This implementation requires get_latest_for_parent_snapshot to determine previous state.
        prev_snapshot = await self._repository.get_latest_for_parent_snapshot(trend_snapshot.snapshot_id)
        if prev_snapshot:
            for symbol_key, sym_res in prev_snapshot.symbols.items():
                ts_keys = {f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}" for ts in context.trend_snapshot.symbols}
                if symbol_key in ts_keys:
                    # In Validation Stage, we instantiate SymbolLifecycleContext.
                    # However, since Validation comes inside pipeline.execute(), 
                    # we can just wait or pre-populate symbol contexts here.
                    # Best to populate here or in validation stage.
                    # Since Engine drives the context setup, we can pre-populate here for efficiency.
                    from backend.trend_engine.lifecycle.pipeline.context import SymbolLifecycleContext
                    context.symbol_contexts[symbol_key] = SymbolLifecycleContext(
                        symbol_key=symbol_key,
                        previous_state=sym_res.final_state
                    )
        
        # Execute pipeline (Validation -> Continuation -> Weakening -> Break -> End -> Aggregation)
        await self._pipeline.execute(context)
        
        # 2. Snapshot Builder
        symbol_results = {}
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            if not sym_ctx.final_state:
                raise LifecycleEvaluationError(f"Missing final state for symbol {symbol_key}.")
                
            symbol_results[symbol_key] = TrendLifecycleSymbolResult(
                symbol_key=symbol_key,
                final_state=sym_ctx.final_state,
                continuation_evidence=sym_ctx.continuation_evidence,
                weakening_evidence=sym_ctx.weakening_evidence,
                break_evidence=sym_ctx.break_evidence,
                end_evidence=sym_ctx.end_evidence
            )
            
        duration_ms = (time.time() - start_time) * 1000.0
        
        # Generate configuration hash
        config_dict = self._config.model_dump()
        config_str = json.dumps(config_dict, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()
        
        # Determine snapshot version
        snapshot_version = 1
        if prev_snapshot:
            snapshot_version = prev_snapshot.snapshot_version + 1
            
        snapshot_id = f"l_{trend_snapshot.snapshot_id}_{snapshot_version}"
        
        snapshot = TrendLifecycleSnapshot(
            snapshot_id=snapshot_id,
            snapshot_version=snapshot_version,
            parent_trend_snapshot_id=trend_snapshot.snapshot_id,
            parent_trend_quality_snapshot_id=quality_snapshot.quality_snapshot_id,
            symbols=symbol_results,
            pipeline_version="1.0.0",
            configuration_hash=config_hash,
            lifecycle_algorithm_version=self._config.lifecycle_algorithm_version,
            lifecycle_rule_version=self._config.lifecycle_rule_version,
            execution_metadata={
                "duration_ms": duration_ms,
                "warnings_count": len(context.warnings),
                "errors_count": len(context.errors)
            },
            audit_metadata={
                "warnings": context.warnings,
                "errors": context.errors
            }
        )
        
        # 3. Repository Persistence
        await self._repository.save_lifecycle_snapshot(snapshot)
        
        # 4. Return Immutable Snapshot
        return snapshot
