from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from backend.trade_validation_engine.trade_decision.config.config import TradeDecisionConfig

class DecisionState(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    REJECTED = "REJECTED"

class RejectionReason(str, Enum):
    VALIDATION_FAILED = "ValidationFailed"
    MISSING_EVIDENCE = "MissingEvidence"
    DATASET_MISMATCH = "DatasetMismatch"
    CONFIGURATION_MISMATCH = "ConfigurationMismatch"
    LINEAGE_BROKEN = "LineageBroken"

class DecisionContext(BaseModel):
    """
    Immutable context passed through the decision pipeline.
    """
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    dataset_version: int = Field(description="Dataset version")
    validation_report_version: str = Field(description="Version/ID of the ValidationReport consumed")
    configuration: TradeDecisionConfig = Field(description="Engine infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata related to this decision run")

    model_config = {"frozen": True}

class DecisionEvidence(BaseModel):
    """
    Contains pure business evidence from a stage.
    """
    evidence_type: str = Field(description="Type of evidence provided")
    verified_properties: Dict[str, Any] = Field(description="Properties verified")

    model_config = {"frozen": True}

class StageExecutionResult(BaseModel):
    """
    Result of a single decision pipeline stage.
    """
    stage_id: str = Field(description="ID of the stage")
    state: DecisionState = Field(description="Proposed decision state from this stage")
    rejection_reasons: List[RejectionReason] = Field(default_factory=list, description="Reasons for rejection if any")
    evidence: Optional[DecisionEvidence] = Field(default=None, description="Business evidence collected")
    execution_duration_ms: int = Field(description="Stage execution duration in ms")
    diagnostics: Dict[str, Any] = Field(default_factory=dict, description="Execution diagnostics/metadata")

    model_config = {"frozen": True}

class TradeDecisionSnapshot(BaseModel):
    """
    Immutable aggregate root representing the final deterministic trade decision.
    """
    decision_id: str = Field(description="Deterministic SHA-256 ID of the decision")
    business_fingerprint: str = Field(description="Deterministic business fingerprint for replay/comparison")
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    dataset_version: int = Field(description="Dataset version")
    validation_report_version: str = Field(description="Source validation report version")
    
    decision_state: DecisionState = Field(description="Final resolved decision state")
    rejection_reasons: List[RejectionReason] = Field(default_factory=list, description="Aggregated rejection reasons")
    stage_results: List[StageExecutionResult] = Field(default_factory=list, description="All stage execution results")
    
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Global metadata")

    model_config = {"frozen": True}
