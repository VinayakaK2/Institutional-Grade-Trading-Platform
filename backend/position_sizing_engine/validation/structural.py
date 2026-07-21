from backend.position_sizing_engine.validation.contracts import IPositionSizingValidationLayer
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.report import ValidationResult

class StructuralValidationLayer(IPositionSizingValidationLayer):
    """
    Validates the structure of the PositionSizingContext.
    Responsible for required fields, null values, positive capital constraints.
    """
    async def validate(self, context: PositionSizingContext) -> ValidationResult:
        errors = []
        
        if not context.parent_risk_snapshot:
            errors.append("Parent risk snapshot reference is required.")
        if context.available_capital <= 0:
            errors.append("Available capital must be strictly positive.")
        if "allocation_pct" not in context.allocation_configuration:
            errors.append("Allocation configuration must contain 'allocation_pct'.")
        if "max_risk_pct" not in context.allocation_configuration:
            errors.append("Allocation configuration must contain 'max_risk_pct'.")
        if not context.configuration:
            errors.append("Configuration is strictly required.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
