from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import GrossNetExposure

class GrossNetExposureStage(IPortfolioExposurePipelineStage):
    """
    Calculates gross, net, long, and short exposure.
    Depends on CapitalExposureStage.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        state = context.execution_context.portfolio_state_snapshot.portfolio_state
        
        long_exposure = 0.0
        short_exposure = 0.0
        
        for p in state.positions:
            pos_value = p.quantity * p.current_price
            if pos_value > 0:
                long_exposure += pos_value
            else:
                short_exposure += abs(pos_value)
                
        gross = long_exposure + short_exposure
        net = long_exposure - short_exposure
        
        gn_exp = GrossNetExposure(
            gross_exposure=gross,
            net_exposure=net,
            long_exposure=long_exposure,
            short_exposure=short_exposure
        )
        
        analysis = context.exposure_analysis.model_copy(update={"gross_net_exposure": gn_exp})
        return context.model_copy(update={"exposure_analysis": analysis})
