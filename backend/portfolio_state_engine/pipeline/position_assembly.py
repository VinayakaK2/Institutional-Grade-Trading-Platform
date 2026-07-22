from backend.portfolio_state_engine.contracts.pipeline import IPortfolioStatePipelineStage
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext

class PositionAssemblyStage(IPortfolioStatePipelineStage):
    """
    Assembles positions from the execution context into the portfolio state.
    """
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        state = context.portfolio_state.model_copy(update={"positions": context.execution_context.positions})
        return context.model_copy(update={"portfolio_state": state})
