from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.metadata import PipelineMetadata

class PortfolioExecutionContext(BaseModel):
    """
    The immutable external API context.
    """
    symbol: str = Field(description="The trading symbol")
    timeframe: str = Field(description="The timeframe resolution")
    dataset_version: str = Field(description="Version of the market dataset")
    parent_snapshot_references: ParentSnapshotReferences = Field(description="Lineage parent snapshots")
    configuration: PortfolioConfiguration = Field(description="Infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary external metadata")
    
    model_config = {"frozen": True}

class PortfolioPipelineContext(BaseModel):
    """
    Internal context passed through the pipeline. Wraps execution context and carries execution metadata.
    """
    execution_context: PortfolioExecutionContext = Field(description="The external context")
    execution_id: str = Field(description="Unique ID for this pipeline execution run")
    stage_timings: Dict[str, float] = Field(default_factory=dict, description="Timings of individual stages")
    pipeline_metadata: Optional[PipelineMetadata] = Field(default=None, description="Metadata populated post-execution")
    diagnostics: Dict[str, Any] = Field(default_factory=dict, description="Internal diagnostics")
    
    model_config = {"frozen": True}
