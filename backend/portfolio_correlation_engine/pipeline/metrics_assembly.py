from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.correlation_models import CorrelationMetrics

class MetricsAssemblyStage(ICorrelationStage):
    """
    Assembles aggregate correlation metrics into a separate model.
    """
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
        analysis = context.correlation_analysis
        
        scores = [
            analysis.symbol_correlation.correlation_score,
            analysis.sector_correlation.correlation_score,
            analysis.industry_correlation.correlation_score,
            analysis.strategy_correlation.correlation_score,
            analysis.directional_correlation.correlation_score
        ]
        
        avg_corr = sum(scores) / len(scores) if scores else 0.0
        max_corr = max(scores) if scores else 0.0
        
        div_score = 100.0 - (avg_corr * 100)
        conc_score = avg_corr * 100
        
        metrics = CorrelationMetrics(
            average_correlation=avg_corr,
            maximum_correlation=max_corr,
            correlation_distribution={"symbol": scores[0], "sector": scores[1], "industry": scores[2], "strategy": scores[3], "directional": scores[4]},
            diversification_score=div_score,
            concentration_score=conc_score
        )
        
        return context.model_copy(update={"correlation_metrics": metrics})
