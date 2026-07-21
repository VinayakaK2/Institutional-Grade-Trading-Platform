import abc
from backend.portfolio_risk_engine.models.context import PortfolioRiskContext
from backend.portfolio_risk_engine.models.report import ValidationResult

class IPortfolioRiskValidationLayer(abc.ABC):
    """
    Contract for Portfolio Risk Engine validation layers.
    """
    @abc.abstractmethod
    async def validate(self, context: PortfolioRiskContext) -> ValidationResult:
        pass
