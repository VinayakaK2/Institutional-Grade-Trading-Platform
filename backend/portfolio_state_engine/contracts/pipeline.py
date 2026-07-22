from abc import ABC, abstractmethod
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext

class IPortfolioStatePipelineStage(ABC):
    """
    Interface for a single stage in the portfolio state pipeline.
    """
    
    @abstractmethod
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        """
        Executes the stage logic to assemble portfolio state and returns the updated context.
        """
        pass
