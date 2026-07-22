from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, StrictStr, ConfigDict

class PaperExecutionConfiguration(BaseModel):
    """
    Immutable configuration for the Paper Execution Engine.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    
    engine_version: StrictStr
    snapshot_version: StrictStr
    pipeline_version: StrictStr
    execution_mode: StrictStr
    validation_level: StrictStr

class PaperExecutionMetadata(BaseModel):
    """
    Immutable metadata associated with an execution request.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    
    request_id: StrictStr
    correlation_id: StrictStr
    created_by: StrictStr
    environment: StrictStr
    notes: Optional[StrictStr] = None

class PaperExecutionContext(BaseModel):
    """
    Immutable input container for the Paper Execution Engine.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    
    symbol: StrictStr
    timeframe: StrictStr
    dataset_version: StrictStr
    parent_portfolio_decision_snapshot_version: StrictStr
    configuration: PaperExecutionConfiguration
    metadata: PaperExecutionMetadata

class PaperExecutionPipelineContext(BaseModel):
    """
    Internal execution state for the pipeline. This object is mutable 
    and handles diagnostic, sharing, and timing states.
    It is never persisted.
    """
    model_config = ConfigDict(extra='forbid')
    
    execution_state: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    shared_objects: Dict[str, Any] = Field(default_factory=dict)
    pipeline_metrics: Dict[str, Any] = Field(default_factory=dict)
    stage_outputs: Dict[str, Any] = Field(default_factory=dict)
