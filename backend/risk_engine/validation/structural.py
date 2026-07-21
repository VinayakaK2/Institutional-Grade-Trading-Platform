from backend.risk_engine.validation.contracts import IValidationLayer
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.models.snapshot import ValidationResult

class StructuralValidationLayer(IValidationLayer):
    """
    Validates the structure of the RiskExecutionContext.
    Responsible for: required fields, type validation, null checks, configuration presence, metadata validation.
    """
    async def validate(self, context: RiskExecutionContext) -> ValidationResult:
        errors = []
        
        # Structural null / type checks
        if not context.symbol:
            errors.append("Symbol cannot be empty.")
            
        if not context.timeframe:
            errors.append("Timeframe cannot be empty.")
            
        if context.dataset_version <= 0:
            errors.append("Dataset version must be strictly positive.")
            
        if not context.parent_trade_decision_snapshot_version:
            errors.append("Parent snapshot version must be provided.")
            
        if not context.configuration:
            errors.append("Configuration is strictly required.")
            
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors)
