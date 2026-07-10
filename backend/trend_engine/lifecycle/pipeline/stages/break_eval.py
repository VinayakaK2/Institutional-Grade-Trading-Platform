from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.models.models import BreakEvidence

class BreakEvaluationStage(ITrendLifecycleStage):
    """
    Evaluates structural invalidations or EMA alignment loss to produce BreakEvidence.
    """
    async def execute(self, context: LifecycleExecutionContext) -> None:
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            try:
                qs = next((q for q in context.quality_snapshot.symbols if q.symbol_key == symbol_key), None)
                if not qs:
                    continue
                    
                c_res = qs.consistency_metrics
                is_broken = False
                reasons = []
                
                # Check for structural invalidations
                if c_res.structural_noise_percent > context.config.max_structural_noise_percent:
                    is_broken = True
                    reasons.append(f"Structural noise ({c_res.structural_noise_percent}%) exceeded maximum allowed ({context.config.max_structural_noise_percent}%).")
                    
                reason_str = " ".join(reasons) if is_broken else "Structure remains valid without breaks."
                
                sym_ctx.break_evidence = BreakEvidence(
                    is_broken=is_broken,
                    reason=reason_str
                )
            except Exception as e:
                context.warnings.append(f"Break eval failed for {symbol_key}: {e}")
                sym_ctx.break_evidence = BreakEvidence(
                    is_broken=False,
                    reason=f"Evaluation failed: {e}"
                )
