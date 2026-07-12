from enum import Enum
import hashlib
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class LiquidityGrabLifecycleState(str, Enum):
    """
    ACTIVE: Default state. Candidate exists. No other lifecycle evidence exceeds its threshold.
    CONTINUING: Positive continuation evidence exists. Candidate remains structurally healthy. No weakening or failure evidence dominates.
    WEAKENING: Candidate still exists. Signs of deterioration have appeared. Failure conditions have not yet been satisfied.
    FAILED: Candidate has become structurally invalid. Recovery is no longer possible. Lifecycle terminates due to invalidation.
    EXPIRED: Candidate naturally exceeded its lifecycle window. No structural failure occurred. Lifecycle ends because the setup became stale.
    """
    ACTIVE = "ACTIVE"
    CONTINUING = "CONTINUING"
    WEAKENING = "WEAKENING"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class LifecycleEvidenceMetadata(BaseModel):
    strategy_version: str
    configuration_hash: str
    evidence_schema_version: str
    
    model_config = ConfigDict(frozen=True)

class ContinuationEvidence(BaseModel):
    metadata: LifecycleEvidenceMetadata
    is_continuing: bool
    reason: Optional[str] = None
    confidence: float
    
    model_config = ConfigDict(frozen=True)

class WeakeningEvidence(BaseModel):
    metadata: LifecycleEvidenceMetadata
    is_weakening: bool
    reason: Optional[str] = None
    confidence: float
    
    model_config = ConfigDict(frozen=True)

class FailureEvidence(BaseModel):
    metadata: LifecycleEvidenceMetadata
    is_failed: bool
    reason: Optional[str] = None
    confidence: float
    
    model_config = ConfigDict(frozen=True)

class ExpirationEvidence(BaseModel):
    metadata: LifecycleEvidenceMetadata
    is_expired: bool
    reason: Optional[str] = None
    confidence: float
    
    model_config = ConfigDict(frozen=True)

class LifecycleEvidence(BaseModel):
    continuation_evidence: Optional[ContinuationEvidence] = None
    weakening_evidence: Optional[WeakeningEvidence] = None
    failure_evidence: Optional[FailureEvidence] = None
    expiration_evidence: Optional[ExpirationEvidence] = None

    model_config = ConfigDict(frozen=True)

class LifecycleSummary(BaseModel):
    state: LiquidityGrabLifecycleState
    aggregator_version: str
    decision_reason: Optional[str] = Field(default=None, description="Dominant evidence reason or ID for debugging")
    
    model_config = ConfigDict(frozen=True)

class LiquidityGrabLifecycleSnapshot(BaseModel):
    snapshot_id: str
    candidate_id: str
    symbol_id: str
    timeframe: str
    evidence: LifecycleEvidence
    summary: LifecycleSummary
    metadata: Dict[str, Any]

    model_config = ConfigDict(frozen=True)

    @staticmethod
    def generate_id(candidate_id: str, dataset_version: int, config_hash: str, aggregator_version: str) -> str:
        payload = f"{candidate_id}_{dataset_version}_{config_hash}_{aggregator_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
