from typing import List
from backend.paper_fill_engine.contracts.pipeline import IPaperFillPipelineStage
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext
import time

class PipelineExecutor:
    """
    Executes a sequence of IPaperFillPipelineStage instances deterministically,
    and captures lightweight stage timings in the pipeline_context.
    """
    def __init__(self, stages: List[IPaperFillPipelineStage] = None):
        self._stages = stages or []

    async def execute(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext) -> None:
        """
        Executes all stages in sequence.
        """
        total_start = time.perf_counter()
        
        for stage in self._stages:
            stage_name = stage.__class__.__name__
            stage_start = time.perf_counter()
            
            await stage.execute(execution_context, pipeline_context)
            
            stage_end = time.perf_counter()
            pipeline_context.telemetry.stage_timings[stage_name] = (stage_end - stage_start) * 1000.0
            
        total_end = time.perf_counter()
        pipeline_context.telemetry.execution_duration_ms = (total_end - total_start) * 1000.0
