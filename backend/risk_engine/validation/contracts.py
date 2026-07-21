import abc
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.models.snapshot import ValidationResult

class IValidationLayer(abc.ABC):
    """
    Contract for Risk Engine validation layers.
    """
    @abc.abstractmethod
    async def validate(self, context: RiskExecutionContext) -> ValidationResult:
        """
        Validates the execution context according to specific layer rules.
        """
        pass
