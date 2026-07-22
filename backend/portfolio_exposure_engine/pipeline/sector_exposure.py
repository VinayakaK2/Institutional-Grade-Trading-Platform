from collections import defaultdict
from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.models.exposure_models import SectorExposure

class SectorExposureStage(IPortfolioExposurePipelineStage):
    """
    Calculates sector exposures and weights.
    Depends on PositionWeightStage.
    """
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
        state = context.execution_context.portfolio_state_snapshot.portfolio_state
        weights = context.exposure_analysis.position_exposure.individual_weights
        from typing import DefaultDict
        exposure_per_sector: DefaultDict[str, float] = defaultdict(float)
        weight_per_sector: DefaultDict[str, float] = defaultdict(float)
        
        for p in state.positions:
            sector = p.sector
            pos_value = p.quantity * p.current_price
            exposure_per_sector[sector] += pos_value
            weight_per_sector[sector] += weights.get(p.symbol, 0.0)
            
        total_sectors = len(weight_per_sector)
        distribution = {}
        if total_sectors > 0:
            for s in weight_per_sector:
                distribution[s] = 100.0 / total_sectors
                
        sec_exp = SectorExposure(
            exposure_per_sector=dict(exposure_per_sector),
            sector_weights=dict(weight_per_sector),
            sector_distribution=distribution
        )
        
        analysis = context.exposure_analysis.model_copy(update={"sector_exposure": sec_exp})
        return context.model_copy(update={"exposure_analysis": analysis})
