import time
from backend.paper_execution_result_engine.models.contexts import (
    PaperExecutionResultExecutionContext, 
    PaperExecutionResultPipelineContext
)
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.validation.structural import StructuralValidator
from backend.paper_execution_result_engine.validation.consistency import ConsistencyValidator
from backend.paper_execution_result_engine.core.stages.status import ExecutionStatusStage
from backend.paper_execution_result_engine.core.stages.summary import ExecutionSummaryStage
from backend.paper_execution_result_engine.core.stages.timeline import ExecutionTimelineStage
from backend.paper_execution_result_engine.builders.snapshot_builder import SnapshotBuilder
from backend.paper_execution_result_engine.logging.logger import PaperExecutionResultLogger, logger

class PaperExecutionResultEngine:
    """
    Orchestrates the resolution of Paper Execution Results without recalculation.
    """
    def __init__(self):
        self.status_stage = ExecutionStatusStage()
        self.summary_stage = ExecutionSummaryStage()
        self.timeline_stage = ExecutionTimelineStage()
        self.builder = SnapshotBuilder()
        
    def execute(self, execution_context: PaperExecutionResultExecutionContext) -> PaperExecutionSnapshot:
        start_time = time.perf_counter()
        
        # 1. Validation
        StructuralValidator.validate(execution_context)
        ConsistencyValidator.validate(execution_context)
        
        pipeline_context = PaperExecutionResultPipelineContext(
            execution_context=execution_context
        )
        
        # 2. Status Resolution
        self._run_stage("status_resolution", self.status_stage.execute, pipeline_context)
        
        # 3. Summary Aggregation
        self._run_stage("summary_aggregation", self.summary_stage.execute, pipeline_context)
        
        # 4. Timeline Generation
        self._run_stage("timeline_generation", self.timeline_stage.execute, pipeline_context)
        
        # 5. Builder
        snapshot = self.builder.build(pipeline_context)
        
        total_time = time.perf_counter() - start_time
        pipeline_context.telemetry.execution_duration_ms = total_time * 1000.0
        
        PaperExecutionResultLogger.log_snapshot_created(snapshot)
        logger.info(f"Execution result pipeline finished in {pipeline_context.telemetry.execution_duration_ms:.2f} ms")
        
        return snapshot
        
    def _run_stage(self, name: str, func, context: PaperExecutionResultPipelineContext) -> None:
        st = time.perf_counter()
        func(context)
        context.telemetry.stage_timings[name] = (time.perf_counter() - st) * 1000.0
