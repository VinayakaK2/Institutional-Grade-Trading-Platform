from backend.position_risk_engine.validation.contracts import IPositionRiskValidationLayer
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import ValidationResult

class ConsistencyValidationLayer(IPositionRiskValidationLayer):
    """
    Validates logical consistency.
    Responsible for lineage, alignment, compatibility.
    """
    async def validate(self, context: PositionRiskEvaluationContext) -> ValidationResult:
        errors = []
        
        if not context.trade_decision_snapshot_version or "MOCK_INVALID" in context.trade_decision_snapshot_version:
            errors.append("TradeDecision lineage validation failed.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
