from backend.portfolio_engine.models.context import PortfolioExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class StructuralValidator:
    """
    Validates required fields, types, and non-null guarantees.
    Returns a ValidationResult instead of throwing.
    """
    
    def validate(self, context: PortfolioExecutionContext) -> ValidationResult:
        if not context.symbol:
            return ValidationResult(is_valid=False, reason="Symbol is required")
        if not context.timeframe:
            return ValidationResult(is_valid=False, reason="Timeframe is required")
        if not context.dataset_version:
            return ValidationResult(is_valid=False, reason="Dataset version is required")
        if not context.parent_snapshot_references.risk_snapshot_version:
            return ValidationResult(is_valid=False, reason="Risk snapshot version is required")
            
        return ValidationResult(is_valid=True)
