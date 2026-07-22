from abc import ABC, abstractmethod
from backend.portfolio_engine.models.context import PortfolioPipelineContext

class IPortfolioPipelineStage(ABC):
    """
    Interface for a single stage in the portfolio pipeline.
    """
    
    @abstractmethod
    async def execute(self, context: PortfolioPipelineContext) -> PortfolioPipelineContext:
        """
        Executes the stage logic and returns the updated context.
        """
        pass
