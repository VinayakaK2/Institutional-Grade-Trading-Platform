from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import SectorCorrelation, PairwiseCorrelation

class SectorCorrelationStage(ICorrelationStage):
    """
    Measures sector correlation and concentration.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        exp_snap = context.execution_context.portfolio_exposure_snapshot
        candidate_snap = context.execution_context.candidate_position_snapshot
        
        cand_sector = candidate_snap.sector
        sector_weights = exp_snap.exposure_analysis.sector_exposure.sector_weights
        
        # Determine concentration
        cand_sector_weight = sector_weights.get(cand_sector, 0.0)
        
        relationships = []
        for sector in sector_weights:
            val = 1.0 if sector == cand_sector else 0.2
            relationships.append(PairwiseCorrelation(
                left_symbol=cand_sector,
                right_symbol=sector,
                correlation=val
            ))
            
        vals = [r.correlation for r in relationships]
        avg_rel = sum(vals) / len(vals) if vals else 0.0
            
        sec_corr = SectorCorrelation(
            correlation_score=avg_rel,
            confidence=0.85,
            candidate_sector_to_portfolio_correlation=cand_sector_weight,
            sector_concentration=cand_sector_weight,
            sector_relationships=tuple(relationships)
        )
        
        new_analysis = context.correlation_analysis.model_copy(update={"sector_correlation": sec_corr})
        return context.model_copy(update={"correlation_analysis": new_analysis})
