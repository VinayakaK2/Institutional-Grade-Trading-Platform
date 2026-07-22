from abc import ABC, abstractmethod
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext

class IPortfolioExposurePipelineStage(ABC):
    """
    Interface for a single stage in the portfolio exposure pipeline.
    """
    @abstractmethod
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        """
        Executes the stage logic to calculate exposure and returns the updated context.
        """
        pass
