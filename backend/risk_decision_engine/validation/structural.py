from backend.risk_decision_engine.validation.contracts import IRiskDecisionValidationLayer
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.report import ValidationResult

class StructuralValidationLayer(IRiskDecisionValidationLayer):
    """
    Validates the structure of the RiskDecisionContext.
    Responsible for required fields, null checks, and configuration presence.
    """
    async def validate(self, context: RiskDecisionContext) -> ValidationResult:
        errors = []
        
        if not context.parent_snapshots:
            errors.append("Parent snapshot references are required.")
        if not context.risk_evaluation_snapshot:
            errors.append("Risk Evaluation Snapshot is required.")
        if not context.position_sizing_snapshot:
            errors.append("Position Sizing Snapshot is required.")
        if not context.portfolio_risk_snapshot:
            errors.append("Portfolio Risk Snapshot is required.")
        if not context.configuration:
            errors.append("Configuration is strictly required.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
