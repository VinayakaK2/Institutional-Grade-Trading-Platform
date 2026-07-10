from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class TrendLifecycleState(str, Enum):
    """
    Lifecycle states of a validated trend over time.
    """
    # Trend exists but has not yet satisfied continuation, weakening, break, or end conditions.
    # Note: This does NOT strictly mean a 'newly detected' trend.
    ACTIVE = "ACTIVE"
    
    CONTINUING = "CONTINUING"
    WEAKENING = "WEAKENING"
    BROKEN = "BROKEN"
    ENDED = "ENDED"

class ContinuationEvidence(BaseModel):
    is_continuing: bool = Field(description="True if the trend is structurally maintaining its trajectory.")
    reason: str = Field(description="Explanation of the evaluation.")

class WeakeningEvidence(BaseModel):
    is_weakening: bool = Field(description="True if the trend is showing signs of objective weakening.")
    reason: str = Field(description="Explanation of the evaluation.")

class BreakEvidence(BaseModel):
    is_broken: bool = Field(description="True if the trend structure is invalid.")
    reason: str = Field(description="Explanation of the evaluation.")

class EndEvidence(BaseModel):
    is_ended: bool = Field(description="True if the trend has completely terminated.")
    reason: str = Field(description="Explanation of the evaluation.")

class TrendLifecycleSymbolResult(BaseModel):
    symbol_key: str = Field(description="Format: SYMBOL:EXCHANGE")
    final_state: TrendLifecycleState = Field(description="The aggregated lifecycle state.")
    
    continuation_evidence: Optional[ContinuationEvidence] = None
    weakening_evidence: Optional[WeakeningEvidence] = None
    break_evidence: Optional[BreakEvidence] = None
    end_evidence: Optional[EndEvidence] = None

class TrendLifecycleMetadata(BaseModel):
    snapshot_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = "Trend Lifecycle Evaluation Snapshot"

class TrendLifecycleSnapshot(BaseModel):
    snapshot_id: str = Field(description="Unique ID for this lifecycle snapshot.")
    snapshot_version: int = Field(default=1)
    
    parent_trend_snapshot_id: str = Field(description="ID of the underlying trend detection snapshot.")
    parent_trend_quality_snapshot_id: str = Field(description="ID of the underlying trend quality snapshot.")
    
    symbols: Dict[str, TrendLifecycleSymbolResult] = Field(description="Lifecycle states per symbol.")
    
    pipeline_version: str = Field(description="Version of the pipeline orchestrator.")
    configuration_hash: str = Field(description="Hash of the config used.")
    lifecycle_algorithm_version: str = Field(description="Algorithm logic version.")
    lifecycle_rule_version: int = Field(description="Rule/Threshold version.")
    
    metadata: TrendLifecycleMetadata = Field(default_factory=TrendLifecycleMetadata)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
    audit_metadata: Dict[str, Any] = Field(default_factory=dict)
