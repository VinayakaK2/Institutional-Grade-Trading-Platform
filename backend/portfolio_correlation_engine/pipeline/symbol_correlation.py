from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import SymbolCorrelation, PairwiseCorrelation

class SymbolCorrelationStage(ICorrelationStage):
    """
    Measures pairwise symbol correlations between candidate and existing portfolio.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        state_snap = context.execution_context.portfolio_state_snapshot
        candidate_snap = context.execution_context.candidate_position_snapshot
        
        pairwise = []
        for pos in state_snap.portfolio_state.positions:
            # Mock calculation: in a real system this would use time series math.
            # For this phase, we just assert deterministic calculation capabilities.
            val = 1.0 if pos.symbol == candidate_snap.symbol else 0.5
            pairwise.append(PairwiseCorrelation(
                left_symbol=candidate_snap.symbol,
                right_symbol=pos.symbol,
                correlation=val
            ))
                
        vals = [p.correlation for p in pairwise]
        avg = sum(vals) / len(vals) if vals else 0.0
        max_c = max(vals) if vals else 0.0
        min_c = min(vals) if vals else 0.0
        
        sym_corr = SymbolCorrelation(
            correlation_score=avg,
            confidence=0.9,
            candidate_to_portfolio_avg=avg,
            candidate_to_portfolio_max=max_c,
            candidate_to_portfolio_min=min_c,
            pairwise_correlations=tuple(pairwise)
        )
        
        new_analysis = context.correlation_analysis.model_copy(update={"symbol_correlation": sym_corr})
        return context.model_copy(update={"correlation_analysis": new_analysis})
