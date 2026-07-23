from backend.paper_execution_quality_engine.contracts.pipeline import IPaperExecutionQualityStage
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import SpreadMetrics

class SpreadStage(IPaperExecutionQualityStage):
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        cfg = execution_context.configuration.get("spread", {})
        
        bid_price = float(cfg.get("bid_price", 0.0))
        ask_price = float(cfg.get("ask_price", 0.0))
        
        mid_price = (bid_price + ask_price) / 2.0 if bid_price and ask_price else 0.0
        
        effective_spread = float(cfg.get("effective_spread", ask_price - bid_price if bid_price and ask_price else 0.0))
        paid_spread = float(cfg.get("paid_spread", effective_spread / 2.0))

        pipeline_context.spread_result = SpreadMetrics(
            bid_price=bid_price,
            ask_price=ask_price,
            mid_price=mid_price,
            effective_spread=effective_spread,
            paid_spread=paid_spread
        )
