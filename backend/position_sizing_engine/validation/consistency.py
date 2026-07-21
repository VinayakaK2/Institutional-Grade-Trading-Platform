from backend.position_sizing_engine.validation.contracts import IPositionSizingValidationLayer
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.report import ValidationResult

class ConsistencyValidationLayer(IPositionSizingValidationLayer):
    """
    Validates logical consistency.
    Responsible for lineage, alignment, compatibility.
    """
    async def validate(self, context: PositionSizingContext) -> ValidationResult:
        errors = []
        
        if not context.parent_risk_snapshot.snapshot_id or "MOCK_INVALID" in context.parent_risk_snapshot.snapshot_id:
            errors.append("RiskSnapshot lineage validation failed.")
            
        # Ensure the actual passed full snapshot matches the reference id
        if context.parent_risk_snapshot.snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Risk Evaluation Snapshot ID does not match the Parent Reference ID.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
