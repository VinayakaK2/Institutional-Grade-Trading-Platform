from backend.position_risk_engine.validation.contracts import IPositionRiskValidationLayer
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import ValidationResult

class StructuralValidationLayer(IPositionRiskValidationLayer):
    """
    Validates the structure of the PositionRiskEvaluationContext.
    Responsible for required fields, null values, price validity, stop-loss validity, config presence.
    """
    async def validate(self, context: PositionRiskEvaluationContext) -> ValidationResult:
        errors = []
        
        if not context.symbol:
            errors.append("Symbol is required.")
        if not context.timeframe:
            errors.append("Timeframe is required.")
        if context.entry_price <= 0:
            errors.append("Entry price must be strictly positive.")
        if context.initial_stop_loss <= 0:
            errors.append("Initial stop loss must be strictly positive.")
        if context.entry_price == context.initial_stop_loss:
            errors.append("Entry price and stop loss cannot be identical.")
        if not context.configuration:
            errors.append("Configuration is strictly required.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
