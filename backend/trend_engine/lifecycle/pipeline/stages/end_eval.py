from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.models.models import EndEvidence
from backend.trend_engine.models.models import TrendDirection

class EndEvaluationStage(ITrendLifecycleStage):
    """
    Evaluates transitions to neutral or opposite direction to produce EndEvidence.
    """
    async def execute(self, context: LifecycleExecutionContext) -> None:
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            try:
                ts = next((t for t in context.trend_snapshot.symbols if f"{t.watchlist_symbol.symbol.symbol}:{t.watchlist_symbol.symbol.exchange.code}" == symbol_key), None)
                if not ts:
                    continue
                    
                is_ended = False
                reasons = []
                
                # Check for trend transition
                if ts.direction in [TrendDirection.UNKNOWN, TrendDirection.SIDEWAYS]:
                    is_ended = True
                    reasons.append("Trend transitioned to a non-trending state.")
                    
                # Note: If we had history, we could check if it transitioned from UPTREND to DOWNTREND.
                # Here, we assume the pipeline determines ENDED if quality drops below a critical threshold as well.
                qs = next((q for q in context.quality_snapshot.symbols if q.symbol_key == symbol_key), None)
                if qs:
                    if qs.normalized_metrics.normalized_strength < context.config.min_quality_score_to_maintain:
                        is_ended = True
                        reasons.append("Normalized strength dropped below terminal maintenance threshold.")
                        
                reason_str = " ".join(reasons) if is_ended else "Trend has not terminated."
                
                sym_ctx.end_evidence = EndEvidence(
                    is_ended=is_ended,
                    reason=reason_str
                )
            except Exception as e:
                context.warnings.append(f"End eval failed for {symbol_key}: {e}")
                sym_ctx.end_evidence = EndEvidence(
                    is_ended=False,
                    reason=f"Evaluation failed: {e}"
                )
