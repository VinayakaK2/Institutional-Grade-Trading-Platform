from backend.portfolio_exposure_engine.models.contexts import PortfolioExposureExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioExposureStructuralRules:
    """
    Validates required fields, non-null properties of the provided inputs.
    """
    def validate(self, context: PortfolioExposureExecutionContext) -> ValidationResult:
        if context.portfolio_state_snapshot is None:
            return ValidationResult(is_valid=False, reason="PortfolioStateSnapshot cannot be None")
        if context.configuration is None:
            return ValidationResult(is_valid=False, reason="Configuration cannot be None")
            
        return ValidationResult(is_valid=True)
