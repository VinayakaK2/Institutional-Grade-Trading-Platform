from backend.portfolio_risk_engine.validation.contracts import IPortfolioRiskValidationLayer
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.report import ValidationResult

class ConsistencyValidationLayer(IPortfolioRiskValidationLayer):
    """
    Validates logical consistency.
    Responsible for lineage, compatibility.
    """
    async def validate(self, context: PortfolioRiskContext) -> ValidationResult:
        errors = []
        
        # Verify lineage alignment between references and actual snapshots
        if context.parent_snapshots.risk_snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Risk Evaluation Snapshot ID does not match the Parent Reference ID.")
            
        if context.parent_snapshots.sizing_snapshot_id != context.position_sizing_snapshot.snapshot_id:
            errors.append("Position Sizing Snapshot ID does not match the Parent Reference ID.")
            
        # Verify internal lineage (Sizing Snapshot MUST depend on the exact same Risk Snapshot)
        if context.position_sizing_snapshot.context.parent_risk_snapshot.snapshot_id != context.risk_evaluation_snapshot.snapshot_id:
            errors.append("Position Sizing Snapshot's parent risk snapshot does not match the provided Risk Evaluation Snapshot.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
