from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, StrictStr, ConfigDict
from backend.paper_execution_quality_engine.models.execution_quality import (
    ExecutionQualityReport, MarketImpactMetrics, SlippageMetrics, 
    SpreadMetrics, GapMetrics, LiquidityMetrics
)

class ParentSnapshotReferences(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    parent_fill_snapshot_version: StrictStr

class PaperExecutionQualityExecutionContext(BaseModel):
    """
    Immutable execution context defining the inputs for an execution quality evaluation.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    symbol: StrictStr
    timeframe: StrictStr
    dataset_version: StrictStr
    parent_snapshot_references: ParentSnapshotReferences
    
    configuration_hash: StrictStr
    execution_quality_model_version: StrictStr
    
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PipelineDiagnostics(BaseModel):
    validation_errors: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)

class PipelineTelemetry(BaseModel):
    execution_duration_ms: float = 0.0
    stage_timings: Dict[str, float] = Field(default_factory=dict)

class PaperExecutionQualityPipelineContext(BaseModel):
    """
    Mutable internal context for the pipeline.
    """
    model_config = ConfigDict(extra="forbid")

    execution_context: PaperExecutionQualityExecutionContext
    
    # Intermediary stage results
    market_impact_result: Optional[MarketImpactMetrics] = None
    slippage_result: Optional[SlippageMetrics] = None
    spread_result: Optional[SpreadMetrics] = None
    gap_result: Optional[GapMetrics] = None
    liquidity_result: Optional[LiquidityMetrics] = None
    
    # Final compiled report
    execution_quality_report: Optional[ExecutionQualityReport] = None
    
    def require_complete(self) -> ExecutionQualityReport:
        if not all([self.market_impact_result, self.slippage_result, self.spread_result, self.gap_result, self.liquidity_result]):
            from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityCalculationError
            raise PaperExecutionQualityCalculationError("One or more stages failed to produce a valid metric result.")
            
        return ExecutionQualityReport(
            market_impact=self.market_impact_result,  # type: ignore
            slippage=self.slippage_result,  # type: ignore
            spread_cost=self.spread_result,  # type: ignore
            gap_cost=self.gap_result,  # type: ignore
            liquidity_metrics=self.liquidity_result  # type: ignore
        )
    
    diagnostics: PipelineDiagnostics = Field(default_factory=PipelineDiagnostics)
    telemetry: PipelineTelemetry = Field(default_factory=PipelineTelemetry)
