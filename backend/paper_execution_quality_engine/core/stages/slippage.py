from backend.paper_execution_quality_engine.contracts.pipeline import IPaperExecutionQualityStage
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import SlippageMetrics

class SlippageStage(IPaperExecutionQualityStage):
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        base_slippage = execution_context.metadata.get("base_slippage", 0.005)
        volatility_modifier = execution_context.simulated_order_data.get("volatility", 1.0)
        
        calculated_slippage = base_slippage * volatility_modifier
        
        pipeline_context.slippage_result = SlippageMetrics(
            expected_price=expected_price,
            actual_fill_price=actual_fill_price,
            slippage_amount=slippage_amount,
            slippage_percentage=slippage_percentage
        )
