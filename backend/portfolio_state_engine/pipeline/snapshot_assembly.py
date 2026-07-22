from backend.portfolio_state_engine.contracts.pipeline import IPortfolioStatePipelineStage
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext
from backend.portfolio_state_engine.exceptions import PortfolioStatePipelineError

class SnapshotAssemblyStage(IPortfolioStatePipelineStage):
    """
    Finalizes the state before snapshotting. Checks for critical integrity issues like duplicate positions.
    """
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        state = context.portfolio_state
        
        # Check for duplicate positions
        symbols = [p.symbol for p in state.positions]
        if len(symbols) != len(set(symbols)):
            raise PortfolioStatePipelineError("Duplicate positions detected in portfolio state.")
            
        # Check for duplicate orders
        order_ids = [o.order_id for o in state.pending_orders]
        if len(order_ids) != len(set(order_ids)):
            raise PortfolioStatePipelineError("Duplicate pending orders detected in portfolio state.")
            
        return context
