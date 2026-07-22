from backend.portfolio_state_engine.contracts.pipeline import IPortfolioStatePipelineStage
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext
from backend.portfolio_state_engine.models.state import PnLSummary

class PnLAssemblyStage(IPortfolioStatePipelineStage):
    """
    Assembles realized and unrealized PnL from the execution context into the portfolio state.
    """
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        pnl = PnLSummary(
            realized_pnl=context.execution_context.realized_pnl,
            unrealized_pnl=context.execution_context.unrealized_pnl
        )
        state = context.portfolio_state.model_copy(update={"pnl": pnl})
        return context.model_copy(update={"portfolio_state": state})
