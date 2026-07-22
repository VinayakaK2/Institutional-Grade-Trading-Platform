from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import PortfolioExposureMetrics

class MetricsAssemblyStage(IPortfolioExposurePipelineStage):
    """
    Assembles aggregate exposure metrics.
    Depends on all prior exposure stages.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        analysis = context.exposure_analysis
        
        largest_sector_weight = max(analysis.sector_exposure.sector_weights.values()) if analysis.sector_exposure.sector_weights else 0.0
        largest_pos_weight = max(analysis.position_exposure.individual_weights.values()) if analysis.position_exposure.individual_weights else 0.0
        
        metrics = PortfolioExposureMetrics(
            total_positions=len(analysis.position_exposure.individual_weights),
            sector_count=len(analysis.sector_exposure.sector_weights),
            industry_count=len(analysis.industry_exposure.industry_weights),
            largest_sector_weight=largest_sector_weight,
            largest_position_weight=largest_pos_weight,
            average_position_weight=analysis.position_exposure.average_position_weight
        )
        
        new_analysis = analysis.model_copy(update={"exposure_metrics": metrics})
        return context.model_copy(update={"exposure_analysis": new_analysis})
