from backend.paper_execution_quality_engine.contracts.pipeline import IExecutionQualityStage
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import MarketImpactMetrics

class MarketImpactStage(IExecutionQualityStage):
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        impact_factor = execution_context.metadata.get("market_impact_factor", 0.001)
        calculated_impact = execution_context.simulated_order_data["order_size"] * impact_factor
        
        pipeline_context.market_impact_result = MarketImpactMetrics(
            expected_execution_price=expected_execution_price,
            market_impact=market_impact,
            impact_percentage=impact_percentage,
            impact_cost=impact_cost
        )
