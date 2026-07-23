from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus, ExecutionSummary, ExecutionTimeline

class PipelineDiagnostics(BaseModel):
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    warnings: list = Field(default_factory=list)

class PipelineTelemetry(BaseModel):
    execution_duration_ms: float = 0.0
    stage_timings: Dict[str, float] = Field(default_factory=dict)

class PaperExecutionResultExecutionContext(BaseModel):
    """
    Immutable container defining the exact deterministic input state.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    dataset_version: str
    configuration_hash: str
    
    portfolio_decision_snapshot: PortfolioDecisionSnapshot
    paper_order_snapshot: PaperOrderSnapshot
    paper_fill_snapshot: PaperFillSnapshot
    paper_execution_quality_snapshot: PaperExecutionQualitySnapshot
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaperExecutionResultPipelineContext(BaseModel):
    """
    Mutable state container used by the engine to accumulate stage results.
    """
    model_config = ConfigDict(extra="forbid")
    
    execution_context: PaperExecutionResultExecutionContext
    
    execution_status: Optional[ExecutionStatus] = None
    execution_summary: Optional[ExecutionSummary] = None
    execution_timeline: Optional[ExecutionTimeline] = None
    
    def require_complete(self) -> tuple:
        if not self.execution_status or not self.execution_summary or not self.execution_timeline:
            from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError
            raise PaperExecutionResultCalculationError("Pipeline failed to produce one or more required components.")
        return self.execution_status, self.execution_summary, self.execution_timeline
    
    diagnostics: PipelineDiagnostics = Field(default_factory=PipelineDiagnostics)
    telemetry: PipelineTelemetry = Field(default_factory=PipelineTelemetry)
