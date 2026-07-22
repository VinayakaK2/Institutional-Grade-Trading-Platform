from typing import Dict, Any
from pydantic import BaseModel, Field, StrictStr, ConfigDict
from backend.paper_order_engine.models.pipeline import PipelineDiagnostics, PipelineTelemetry
from backend.paper_order_engine.models.order import OrderState

class PaperOrderExecutionContext(BaseModel):
    """
    Immutable execution context defining the input boundaries for an order simulation.
    No runtime state.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    symbol: StrictStr = Field(..., description="The asset symbol (e.g. AAPL)")
    timeframe: StrictStr = Field(..., description="The execution timeframe (e.g. 1D, 1H)")
    dataset_version: StrictStr = Field(..., description="The dataset schema/version reference")
    parent_portfolio_decision_snapshot_version: StrictStr = Field(..., description="Lineage reference to the portfolio decision")
    parent_paper_execution_snapshot_version: StrictStr = Field(..., description="Lineage reference to the paper execution snapshot")
    
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters for the order")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata for the order")

class PaperOrderPipelineContext(BaseModel):
    """
    Mutable internal context for the pipeline.
    Never persisted into the final snapshot.
    """
    model_config = ConfigDict(extra="forbid")

    execution_context: PaperOrderExecutionContext = Field(..., description="The validated execution context")
    intermediate_order_state: OrderState = Field(default=OrderState.CREATED, description="The mutable order state during pipeline execution")
    
    diagnostics: PipelineDiagnostics = Field(default_factory=PipelineDiagnostics)
    telemetry: PipelineTelemetry = Field(default_factory=PipelineTelemetry)
    
    stage_outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs from individual stages")
