import abc
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import ValidationResult

class IPositionRiskValidationLayer(abc.ABC):
    """
    Contract for Position Risk Engine validation layers.
    """
    @abc.abstractmethod
    async def validate(self, context: PositionRiskEvaluationContext) -> ValidationResult:
        pass
