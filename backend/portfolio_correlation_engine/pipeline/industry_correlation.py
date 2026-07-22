from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import IndustryCorrelation, PairwiseCorrelation

class IndustryCorrelationStage(ICorrelationStage):
    """
    Measures industry correlation and concentration.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        exp_snap = context.execution_context.portfolio_exposure_snapshot
        candidate_snap = context.execution_context.candidate_position_snapshot
        
        cand_ind = candidate_snap.industry
        ind_weights = exp_snap.exposure_analysis.industry_exposure.industry_weights
        
        cand_ind_weight = ind_weights.get(cand_ind, 0.0)
        
        relationships = []
        for ind in ind_weights:
            val = 1.0 if ind == cand_ind else 0.1
            relationships.append(PairwiseCorrelation(
                left_symbol=cand_ind,
                right_symbol=ind,
                correlation=val
            ))
            
        vals = [r.correlation for r in relationships]
        avg_rel = sum(vals) / len(vals) if vals else 0.0
            
        ind_corr = IndustryCorrelation(
            correlation_score=avg_rel,
            confidence=0.8,
            candidate_industry_to_portfolio_correlation=cand_ind_weight,
            industry_concentration=cand_ind_weight,
            industry_relationships=tuple(relationships)
        )
        
        new_analysis = context.correlation_analysis.model_copy(update={"industry_correlation": ind_corr})
        return context.model_copy(update={"correlation_analysis": new_analysis})
