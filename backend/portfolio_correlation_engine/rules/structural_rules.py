from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioCorrelationStructuralRules:
    """
    Validates required fields, non-null properties of the provided inputs.
    """
    def validate(self, context: PortfolioCorrelationExecutionContext) -> ValidationResult:
        if context.portfolio_state_snapshot is None:
            return ValidationResult(is_valid=False, reason="PortfolioStateSnapshot cannot be None")
        if context.portfolio_exposure_snapshot is None:
            return ValidationResult(is_valid=False, reason="PortfolioExposureSnapshot cannot be None")
        if context.candidate_position_snapshot is None:
            return ValidationResult(is_valid=False, reason="CandidatePositionSnapshot cannot be None")
        if context.risk_decision_snapshot is None:
            return ValidationResult(is_valid=False, reason="RiskDecisionSnapshot cannot be None")
        if context.configuration is None:
            return ValidationResult(is_valid=False, reason="Configuration cannot be None")
            
        return ValidationResult(is_valid=True)
