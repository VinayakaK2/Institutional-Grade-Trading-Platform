from backend.portfolio_risk_engine.validation.contracts import IPortfolioRiskValidationLayer
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.report import ValidationResult

class StructuralValidationLayer(IPortfolioRiskValidationLayer):
    """
    Validates the structure of the PortfolioRiskContext.
    Responsible for required fields, null values, type validation.
    """
    async def validate(self, context: PortfolioRiskContext) -> ValidationResult:
        errors = []
        
        if not context.parent_snapshots:
            errors.append("Parent snapshot references are required.")
        if not context.risk_evaluation_snapshot:
            errors.append("Risk Evaluation Snapshot is required.")
        if not context.position_sizing_snapshot:
            errors.append("Position Sizing Snapshot is required.")
        if not context.configuration:
            errors.append("Configuration is strictly required.")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
