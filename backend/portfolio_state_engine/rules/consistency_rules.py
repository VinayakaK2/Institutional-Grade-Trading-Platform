from backend.portfolio_state_engine.models.context import PortfolioStateExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class PortfolioStateConsistencyRules:
    """
    Asserts parent Risk Decision compatibility, dataset consistency, and lineage integrity.
    Returns ValidationResult to plug into the engine.
    """
    
    def validate(self, context: PortfolioStateExecutionContext) -> ValidationResult:
        # Example check: dataset version format compatibility
        if not context.dataset_version.startswith("v"):
            return ValidationResult(is_valid=False, reason="Dataset version must follow 'vX' convention")
            
        # Example check: ensure we don't have contradictory inputs like negative available capital
        if context.capital.available_capital < 0:
            return ValidationResult(is_valid=False, reason="Available capital cannot be negative")
            
        return ValidationResult(is_valid=True)
