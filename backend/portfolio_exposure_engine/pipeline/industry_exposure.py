from collections import defaultdict
from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import IndustryExposure

class IndustryExposureStage(IPortfolioExposurePipelineStage):
    """
    Calculates industry exposures and weights.
    Depends on PositionWeightStage.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        state = context.execution_context.portfolio_state_snapshot.portfolio_state
        weights = context.exposure_analysis.position_exposure.individual_weights
        from typing import DefaultDict
        exposure_per_industry: DefaultDict[str, float] = defaultdict(float)
        weight_per_industry: DefaultDict[str, float] = defaultdict(float)
        
        for p in state.positions:
            industry = p.industry
            pos_value = p.quantity * p.current_price
            exposure_per_industry[industry] += pos_value
            weight_per_industry[industry] += weights.get(p.symbol, 0.0)
            
        total_industries = len(weight_per_industry)
        distribution = {}
        if total_industries > 0:
            for i in weight_per_industry:
                distribution[i] = 100.0 / total_industries
                
        ind_exp = IndustryExposure(
            exposure_per_industry=dict(exposure_per_industry),
            industry_weights=dict(weight_per_industry),
            industry_distribution=distribution
        )
        
        analysis = context.exposure_analysis.model_copy(update={"industry_exposure": ind_exp})
        return context.model_copy(update={"exposure_analysis": analysis})
