from abc import ABC, abstractmethod
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationPipelineContext

class IPortfolioOptimizationStage(ABC):
    """
    Contract for a stateless optimization pipeline stage.
    """
    
    @abstractmethod
    async def execute(self, context: PortfolioOptimizationPipelineContext) -> PortfolioOptimizationPipelineContext:
        """
        Executes the stage logic asynchronously and returns the mutated pipeline context.
        """
        pass
