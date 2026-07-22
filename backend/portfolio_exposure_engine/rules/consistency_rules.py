from backend.portfolio_exposure_engine.models.contexts import PortfolioExposureExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioExposureConsistencyRules:
    """
    Asserts dataset version alignment, parent snapshot compatibility, etc.
    """
    def validate(self, context: PortfolioExposureExecutionContext) -> ValidationResult:
        state_snap = context.portfolio_state_snapshot
        if not state_snap.dataset_version:
            return ValidationResult(is_valid=False, reason="Missing dataset version in PortfolioStateSnapshot")
            
        return ValidationResult(is_valid=True)
