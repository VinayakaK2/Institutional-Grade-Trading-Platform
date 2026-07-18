from typing import List, Tuple
from backend.trade_validation_engine.trade_decision.models.models import (
    StageExecutionResult, 
    DecisionState, 
    RejectionReason
)

class DecisionResolver:
    """
    Aggregates all Decision Stage results, applies deterministic precedence rules, 
    resolves conflicts, and produces the final DecisionState and RejectionReasons.
    """
    
    PRECEDENCE = {
        DecisionState.REJECTED: 3,
        DecisionState.INVALID: 2,
        DecisionState.VALID: 1
    }
    
    @staticmethod
    def resolve(stage_results: List[StageExecutionResult]) -> Tuple[DecisionState, List[RejectionReason]]:
        if not stage_results:
            return DecisionState.INVALID, [RejectionReason.VALIDATION_FAILED]
            
        rejection_reasons: List[RejectionReason] = []
        highest_state = DecisionState.VALID
        
        for result in stage_results:
            if DecisionResolver.PRECEDENCE[result.state] > DecisionResolver.PRECEDENCE[highest_state]:
                highest_state = result.state
                
            if result.rejection_reasons:
                rejection_reasons.extend(result.rejection_reasons)
                
        # Deduplicate rejection reasons while preserving order
        seen = set()
        unique_reasons = []
        for r in rejection_reasons:
            if r not in seen:
                seen.add(r)
                unique_reasons.append(r)
                
        return highest_state, unique_reasons
