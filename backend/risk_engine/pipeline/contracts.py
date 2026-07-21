import abc
from typing import Dict, Any
from backend.risk_engine.models.context import RiskExecutionContext

class IRiskPipelineStage(abc.ABC):
    """
    Contract for a risk pipeline stage.
    """
    @property
    @abc.abstractmethod
    def stage_name(self) -> str:
        pass
        
    @abc.abstractmethod
    async def execute(self, context: RiskExecutionContext) -> Dict[str, Any]:
        """
        Executes the stage logic and returns the stage-specific output payload.
        """
        pass
