from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext, SymbolLifecycleContext
from backend.trend_engine.lifecycle.exceptions import LifecycleEvaluationError

class LifecycleValidationStage(ITrendLifecycleStage):
    """
    Validates prerequisites before evaluation begins.
    Ensures that parent snapshots align and populates the symbol contexts.
    """
    async def execute(self, context: LifecycleExecutionContext) -> None:
        try:
            if context.trend_snapshot.snapshot_id != context.quality_snapshot.source_trend_snapshot_id:
                raise LifecycleEvaluationError(
                    f"Quality snapshot parent {context.quality_snapshot.source_trend_snapshot_id} "
                    f"does not match Trend snapshot {context.trend_snapshot.snapshot_id}"
                )
                
            qs_keys = {q.symbol_key for q in context.quality_snapshot.symbols}
            
            for ts in context.trend_snapshot.symbols:
                symbol_key = f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}"
                
                if symbol_key not in qs_keys:
                    context.warnings.append(f"Symbol {symbol_key} missing in Quality Snapshot.")
                    continue
                    
                context.symbol_contexts[symbol_key] = SymbolLifecycleContext(
                    symbol_key=symbol_key
                )
                
        except Exception as e:
            raise LifecycleEvaluationError(f"Validation failed: {str(e)}") from e
