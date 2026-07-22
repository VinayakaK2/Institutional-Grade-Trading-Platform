from backend.portfolio_state_engine.models.context import PortfolioStateExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioStateStructuralRules:
    """
    Validates required fields, non-null properties, and types of the provided inputs.
    Returns ValidationResult to plug into the engine.
    """
    
    def validate(self, context: PortfolioStateExecutionContext) -> ValidationResult:
        if context.positions is None:
            return ValidationResult(is_valid=False, reason="Positions list cannot be None")
        if context.pending_orders is None:
            return ValidationResult(is_valid=False, reason="Pending orders list cannot be None")
        if context.capital is None:
            return ValidationResult(is_valid=False, reason="Capital summary cannot be None")
            
        if not context.dataset_version:
            return ValidationResult(is_valid=False, reason="Dataset version is required")
        if not context.parent_snapshot_references or not context.parent_snapshot_references.risk_snapshot_version:
            return ValidationResult(is_valid=False, reason="Parent risk snapshot version is required")
            
        return ValidationResult(is_valid=True)
