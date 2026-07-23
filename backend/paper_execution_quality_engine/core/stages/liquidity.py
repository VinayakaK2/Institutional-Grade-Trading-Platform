from backend.paper_execution_quality_engine.contracts.pipeline import IPaperExecutionQualityStage
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import LiquidityMetrics

class LiquidityStage(IPaperExecutionQualityStage):
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        cfg = execution_context.configuration.get("liquidity", {})
        
        available_liquidity = float(cfg.get("available_liquidity", 0.0))
        executed_quantity = float(cfg.get("executed_quantity", 0.0))
        
        remaining_liquidity = max(0.0, available_liquidity - executed_quantity)
        
        if available_liquidity > 0:
            liquidity_utilization = (executed_quantity / available_liquidity) * 100.0
        else:
            liquidity_utilization = 0.0

        pipeline_context.liquidity_result = LiquidityMetrics(
            available_liquidity=available_liquidity,
            executed_quantity=executed_quantity,
            remaining_liquidity=remaining_liquidity,
            liquidity_utilization=liquidity_utilization
        )
