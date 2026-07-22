from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioCorrelationConsistencyRules:
    """
    Asserts dataset version alignment, parent snapshot compatibility, etc.
    """
    def validate(self, context: PortfolioCorrelationExecutionContext) -> ValidationResult:
        state_ds = context.portfolio_state_snapshot.dataset_version
        exp_ds = context.portfolio_exposure_snapshot.dataset_version
        cand_ds = context.candidate_position_snapshot.dataset_version
        
        if not (state_ds == exp_ds == cand_ds):
            return ValidationResult(is_valid=False, reason="Dataset version mismatch across parent snapshots")
            
        return ValidationResult(is_valid=True)
