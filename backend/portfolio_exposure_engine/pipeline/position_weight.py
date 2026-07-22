from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import PositionExposure

class PositionWeightStage(IPortfolioExposurePipelineStage):
    """
    Calculates individual position weights, largest, smallest, and average weight.
    Depends on CapitalExposureStage.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        state = context.execution_context.portfolio_state_snapshot.portfolio_state
        cap_exp = context.exposure_analysis.capital_exposure
        
        total_value = cap_exp.total_invested_capital + cap_exp.available_capital
        
        weights = {}
        for p in state.positions:
            pos_value = p.quantity * p.current_price
            if total_value > 0:
                weights[p.symbol] = (pos_value / total_value) * 100.0
            else:
                weights[p.symbol] = 0.0
                
        largest_sym = max(weights, key=lambda k: weights[k]) if weights else ""
        smallest_sym = min(weights, key=lambda k: weights[k]) if weights else ""
        avg_weight = sum(weights.values()) / len(weights) if weights else 0.0
        
        pos_exp = PositionExposure(
            individual_weights=weights,
            largest_position=largest_sym,
            smallest_position=smallest_sym,
            average_position_weight=avg_weight
        )
        
        analysis = context.exposure_analysis.model_copy(update={"position_exposure": pos_exp})
        return context.model_copy(update={"exposure_analysis": analysis})
