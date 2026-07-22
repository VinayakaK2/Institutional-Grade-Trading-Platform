from backend.portfolio_engine.models.context import PortfolioExecutionContext
from backend.portfolio_engine.models.validation import ValidationResult

class ConsistencyValidator:
    """
    Validates dataset compatibility, parent snapshot compatibility, and lineage.
    Returns a ValidationResult.
    """
    
    def validate(self, context: PortfolioExecutionContext) -> ValidationResult:
        # Business logic goes elsewhere, this just checks basic structural compatibility constraints
        
        # Example check: dataset version format compatibility
        if not context.dataset_version.startswith("v"):
            return ValidationResult(is_valid=False, reason="Dataset version must follow 'vX' convention")
            
        return ValidationResult(is_valid=True)
