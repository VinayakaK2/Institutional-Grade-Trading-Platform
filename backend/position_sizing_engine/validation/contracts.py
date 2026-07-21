import abc
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.report import ValidationResult

class IPositionSizingValidationLayer(abc.ABC):
    """
    Contract for Position Sizing Engine validation layers.
    """
    @abc.abstractmethod
    async def validate(self, context: PositionSizingContext) -> ValidationResult:
        pass
