from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import StrategyCorrelation

class StrategyCorrelationStage(ICorrelationStage):
    """
    Measures strategy correlation, overlap, and diversification.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        state_snap = context.execution_context.portfolio_state_snapshot
        candidate_snap = context.execution_context.candidate_position_snapshot
        
        
        strat_overlap = 0.0
        strat_count = 0
        for p in state_snap.portfolio_state.positions:
            strat_count += 1
            # Mocking strategy extraction since OpenPosition in 12.2 doesn't have it explicitly.
            # In a real scenario, this metadata would be mapped or passed along.
            # Assuming metadata strat or just checking symbol for mock.
            if p.symbol == candidate_snap.symbol:
                strat_overlap += 1.0
                
        overlap_percent = strat_overlap / strat_count if strat_count > 0 else 0.0
        diversification = 100.0 - (overlap_percent * 100)
        
        strat_corr = StrategyCorrelation(
            correlation_score=overlap_percent,
            confidence=0.9,
            strategy_overlap=overlap_percent * 100,
            strategy_diversification=diversification,
            strategy_concentration=overlap_percent * 100
        )
        
        new_analysis = context.correlation_analysis.model_copy(update={"strategy_correlation": strat_corr})
        return context.model_copy(update={"correlation_analysis": new_analysis})
