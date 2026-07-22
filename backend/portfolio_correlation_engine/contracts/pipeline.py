from abc import ABC, abstractmethod
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext

class ICorrelationStage(ABC):
    """
    Interface for a single stage in the portfolio correlation pipeline.
    """
    @abstractmethod
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        """
        Executes the stage logic to calculate correlation and returns the updated context.
        """
        pass
