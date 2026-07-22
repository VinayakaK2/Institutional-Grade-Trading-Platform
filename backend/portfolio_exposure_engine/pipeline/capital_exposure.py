from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import CapitalExposure

class CapitalExposureStage(IPortfolioExposurePipelineStage):
    """
    Calculates total invested capital, available capital, utilization, and cash allocation.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        state = context.execution_context.portfolio_state_snapshot.portfolio_state
        
        # Calculate invested capital from open positions
        invested = sum([p.quantity * p.current_price for p in state.positions])
        
        # Assuming available_capital in state.capital is the total portfolio capital available
        total_portfolio_value = state.capital.available_capital + invested
        
        if total_portfolio_value > 0:
            utilization = (invested / total_portfolio_value) * 100.0
            cash_allocation = (state.capital.available_capital / total_portfolio_value) * 100.0
        else:
            utilization = 0.0
            cash_allocation = 100.0 if state.capital.available_capital >= 0 else 0.0
            
        cap_exp = CapitalExposure(
            total_invested_capital=invested,
            available_capital=state.capital.available_capital,
            capital_utilization_percent=utilization,
            cash_allocation=cash_allocation
        )
        
        analysis = context.exposure_analysis.model_copy(update={"capital_exposure": cap_exp})
        return context.model_copy(update={"exposure_analysis": analysis})
