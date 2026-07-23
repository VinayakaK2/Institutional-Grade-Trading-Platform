from backend.paper_execution_quality_engine.contracts.pipeline import IPaperExecutionQualityStage
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import GapMetrics

class GapStage(IPaperExecutionQualityStage):
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        cfg = execution_context.configuration.get("gap", {})
        
        gap_up = bool(cfg.get("gap_up", False))
        gap_down = bool(cfg.get("gap_down", False))
        gap_size = float(cfg.get("gap_size", 0.0))
        gap_impact = float(cfg.get("gap_impact", 0.0))

        pipeline_context.gap_result = GapMetrics(
            gap_up=gap_up,
            gap_down=gap_down,
            gap_size=gap_size,
            gap_impact=gap_impact
        )
