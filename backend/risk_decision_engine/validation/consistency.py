from backend.risk_decision_engine.validation.contracts import IRiskDecisionValidationLayer
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.report import ValidationResult

class ConsistencyValidationLayer(IRiskDecisionValidationLayer):
    """
    Validates logical consistency and lineage compatibility.
    """
    async def validate(self, context: RiskDecisionContext) -> ValidationResult:
        errors = []
        
        # Lineage Alignment (Parent IDs must match the actual snapshots provided)
        if context.parent_snapshots.risk_snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Risk Evaluation Snapshot ID does not match the Parent Reference ID.")
            
        if context.parent_snapshots.sizing_snapshot_id != context.position_sizing_snapshot.snapshot_id:
            errors.append("Position Sizing Snapshot ID does not match the Parent Reference ID.")
            
        if context.parent_snapshots.portfolio_snapshot_id != context.portfolio_risk_snapshot.snapshot_id:
            errors.append("Portfolio Risk Snapshot ID does not match the Parent Reference ID.")
            
        # Internal Lineage Consistency (Sizing and Portfolio must depend on the same Risk Snapshot)
        if context.position_sizing_snapshot.context.parent_risk_snapshot.snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Position Sizing Snapshot's parent risk snapshot does not match the provided Risk Evaluation Snapshot.")
            
        if context.portfolio_risk_snapshot.context.parent_snapshots.risk_snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Portfolio Risk Snapshot's parent risk snapshot does not match the provided Risk Evaluation Snapshot.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
