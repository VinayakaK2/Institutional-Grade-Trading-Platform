from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.models.models import ContinuationEvidence

class ContinuationEvaluationStage(ITrendLifecycleStage):
    """
    Evaluates continuation criteria to produce ContinuationEvidence.
    """
    async def execute(self, context: LifecycleExecutionContext) -> None:
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            try:
                qs = next((q for q in context.quality_snapshot.symbols if q.symbol_key == symbol_key), None)
                if not qs:
                    continue
                    
                # Basic continuation logic: Quality remains above a minimum threshold
                norm = qs.normalized_metrics
                is_continuing = norm.normalized_strength > 0 and norm.normalized_consistency > 0
                reason = "Trend is structurally maintaining its trajectory." if is_continuing else "Lacks sufficient structural consistency."
                
                sym_ctx.continuation_evidence = ContinuationEvidence(
                    is_continuing=is_continuing,
                    reason=reason
                )
            except Exception as e:
                context.warnings.append(f"Continuation eval failed for {symbol_key}: {e}")
                sym_ctx.continuation_evidence = ContinuationEvidence(
                    is_continuing=False,
                    reason=f"Evaluation failed: {e}"
                )
