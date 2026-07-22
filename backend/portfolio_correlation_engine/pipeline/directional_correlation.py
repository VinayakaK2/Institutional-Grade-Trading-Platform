from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import DirectionalCorrelation

class DirectionalCorrelationStage(ICorrelationStage):
    """
    Measures directional exposure correlation.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        exp_snap = context.execution_context.portfolio_exposure_snapshot
        candidate_snap = context.execution_context.candidate_position_snapshot
        
        cand_dir = candidate_snap.direction.lower()
        gn_exp = exp_snap.exposure_analysis.gross_net_exposure
        
        # If portfolio is all long, and candidate is long, correlation is high
        total_gross = gn_exp.gross_exposure
        long_pct = gn_exp.long_exposure / total_gross if total_gross > 0 else 0.0
        short_pct = gn_exp.short_exposure / total_gross if total_gross > 0 else 0.0
        
        if cand_dir == "long":
            corr = long_pct
        elif cand_dir == "short":
            corr = short_pct
        else:
            corr = 0.5
            
        dir_corr = DirectionalCorrelation(
            correlation_score=corr,
            confidence=0.9,
            long_exposure_correlation=long_pct,
            short_exposure_correlation=short_pct,
            net_directional_concentration=corr * 100
        )
        
        new_analysis = context.correlation_analysis.model_copy(update={"directional_correlation": dir_corr})
        return context.model_copy(update={"correlation_analysis": new_analysis})
