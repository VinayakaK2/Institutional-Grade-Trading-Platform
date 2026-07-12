from abc import ABC, abstractmethod
from backend.liquidity_grab_engine.models.models import LiquidityGrabExecutionContext, LiquidityGrabSnapshot

class ILiquidityGrabStage(ABC):
    """
    Contract for a Liquidity Grab Engine pipeline stage.
    """
    
    @abstractmethod
    def execute(self, context: LiquidityGrabExecutionContext, snapshot: LiquidityGrabSnapshot) -> LiquidityGrabSnapshot:
        """
        Executes the stage logic and returns an updated snapshot.
        Must be deterministic and avoid mutating the input snapshot directly where possible.
        """
        pass
