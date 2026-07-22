from backend.portfolio_optimization_engine.contracts.pipeline import IPortfolioOptimizationStage
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationPipelineContext

class PortfolioOptimizationAggregationStage(IPortfolioOptimizationStage):
    """
    Lightweight stage that aggregates upstream facts relevant to optimization.
    No calculations or recomputations are performed here.
    """
    async def execute(self, context: PortfolioOptimizationPipelineContext) -> PortfolioOptimizationPipelineContext:
        aggregated_facts = {
            "portfolio_state_id": context.execution_context.portfolio_state_snapshot.snapshot_id,
            "portfolio_exposure_id": context.execution_context.portfolio_exposure_snapshot.snapshot_id,
            "portfolio_decision": str(context.execution_context.portfolio_decision_snapshot.decision),
            "optimization_targets": context.execution_context.configuration.optimization_targets
        }
        
        context.aggregated_facts.update(aggregated_facts)
        return context
