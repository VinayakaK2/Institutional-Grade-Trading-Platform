from backend.portfolio_state_engine.contracts.pipeline import IPortfolioStatePipelineStage
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext

class CapitalAssemblyStage(IPortfolioStatePipelineStage):
    """
    Assembles capital from the execution context into the portfolio state.
    """
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        state = context.portfolio_state.model_copy(update={"capital": context.execution_context.capital})
        return context.model_copy(update={"portfolio_state": state})
