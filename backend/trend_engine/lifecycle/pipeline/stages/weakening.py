from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.models.models import WeakeningEvidence

class WeakeningEvaluationStage(ITrendLifecycleStage):
    """
    Evaluates weakening criteria (e.g., reduced EMA separation, declining quality)
    to produce WeakeningEvidence.
    """
    async def execute(self, context: LifecycleExecutionContext) -> None:
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            try:
                qs = next((q for q in context.quality_snapshot.symbols if q.symbol_key == symbol_key), None)
                if not qs:
                    continue
                    
                s_res = qs.strength_metrics
                is_weakening = False
                reasons = []
                
                # Check EMA separation ratio threshold
                if s_res.ema_separation_ratio < (context.config.weakening_ema_separation_ratio_threshold / 100.0):
                    is_weakening = True
                    reasons.append("EMA separation dropped below weakening threshold.")
                    
                # Quality drop check could be added here if we passed in historical snapshots
                
                reason_str = " ".join(reasons) if is_weakening else "No objective signs of weakening."
                
                sym_ctx.weakening_evidence = WeakeningEvidence(
                    is_weakening=is_weakening,
                    reason=reason_str
                )
            except Exception as e:
                context.warnings.append(f"Weakening eval failed for {symbol_key}: {e}")
                sym_ctx.weakening_evidence = WeakeningEvidence(
                    is_weakening=False,
                    reason=f"Evaluation failed: {e}"
                )
