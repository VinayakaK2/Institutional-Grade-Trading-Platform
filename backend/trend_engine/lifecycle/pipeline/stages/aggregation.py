from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState

class AggregationEvaluationStage(ITrendLifecycleStage):
    """
    Consolidates evidence to assign the definitive TrendLifecycleState using deterministic precedence:
    ENDED > BROKEN > WEAKENING > CONTINUING > ACTIVE
    """
    
    # Priority mapping (higher number = higher priority)
    _PRIORITY = {
        TrendLifecycleState.ACTIVE: 0,
        TrendLifecycleState.CONTINUING: 1,
        TrendLifecycleState.WEAKENING: 2,
        TrendLifecycleState.BROKEN: 3,
        TrendLifecycleState.ENDED: 4
    }
    
    async def execute(self, context: LifecycleExecutionContext) -> None:
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            try:
                # Validate evidence exists
                if not all([sym_ctx.continuation_evidence, sym_ctx.weakening_evidence, sym_ctx.break_evidence, sym_ctx.end_evidence]):
                    context.warnings.append(f"Missing evidence for symbol {symbol_key}")
                    sym_ctx.final_state = TrendLifecycleState.ACTIVE
                    continue
                
                # Determine state from evidence
                candidate_state = TrendLifecycleState.ACTIVE
                
                if sym_ctx.continuation_evidence.is_continuing: # type: ignore
                    candidate_state = TrendLifecycleState.CONTINUING
                    
                if sym_ctx.weakening_evidence.is_weakening: # type: ignore
                    if self._PRIORITY[TrendLifecycleState.WEAKENING] > self._PRIORITY[candidate_state]:
                        candidate_state = TrendLifecycleState.WEAKENING
                        
                if sym_ctx.break_evidence.is_broken: # type: ignore
                    if self._PRIORITY[TrendLifecycleState.BROKEN] > self._PRIORITY[candidate_state]:
                        candidate_state = TrendLifecycleState.BROKEN
                        
                if sym_ctx.end_evidence.is_ended: # type: ignore
                    if self._PRIORITY[TrendLifecycleState.ENDED] > self._PRIORITY[candidate_state]:
                        candidate_state = TrendLifecycleState.ENDED
                
                # Validate Transition
                # Allowed: ACTIVE -> CONTINUING, CONTINUING -> WEAKENING, WEAKENING -> CONTINUING, 
                # WEAKENING -> BROKEN, BROKEN -> ENDED, CONTINUING -> ENDED
                # Rejected: ENDED -> CONTINUING, ENDED -> ACTIVE
                prev_state = sym_ctx.previous_state
                
                if prev_state == TrendLifecycleState.ENDED and candidate_state != TrendLifecycleState.ENDED:
                    # Once ENDED, it remains ENDED forever (for that specific trend snapshot lineage).
                    # A new trend would generate a completely new TrendSnapshot ID, bypassing this.
                    candidate_state = TrendLifecycleState.ENDED
                    context.warnings.append(f"Attempted to revive ENDED trend for {symbol_key}. Forcing ENDED.")
                
                sym_ctx.final_state = candidate_state
                
            except Exception as e:
                context.warnings.append(f"Aggregation failed for {symbol_key}: {e}")
                sym_ctx.final_state = TrendLifecycleState.ACTIVE
