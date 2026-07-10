import hashlib
from enum import Enum
from datetime import datetime, timezone
from typing import List, Any, Dict
from pydantic import BaseModel, Field

from backend.consolidation_engine.models.models import ConsolidationCandidate
from backend.consolidation_engine.quality.models import ConsolidationQualityReport
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.lifecycle.config import ConsolidationLifecycleConfiguration


class ConsolidationLifecycleState(str, Enum):
    """
    Deterministic states defining the lifecycle evolution of a candidate.
    NOTE: 'ENDED' is a strictly terminal state. Once ENDED is reached, 
    the consolidation should never transition back to ACTIVE or CONTINUING.
    """
    ACTIVE = "ACTIVE"
    CONTINUING = "CONTINUING"
    WEAKENING = "WEAKENING"
    BROKEN = "BROKEN"
    ENDED = "ENDED"

class BaseLifecycleEvidence(BaseModel):
    triggered: bool
    confidence: float = Field(description="Supporting metadata only. NOT used to choose lifecycle state.")
    reason: str
    supporting_metrics: Dict[str, Any] = Field(default_factory=dict)
    evaluation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"frozen": True}

class ContinuationEvidence(BaseLifecycleEvidence):
    pass

class WeakeningEvidence(BaseLifecycleEvidence):
    pass

class BreakEvidence(BaseLifecycleEvidence):
    pass

class EndEvidence(BaseLifecycleEvidence):
    pass

class ConsolidationLifecycleContext(BaseModel):
    """
    Immutable context for lifecycle evaluation.
    'evaluation_candles' contains ONLY candles occurring AFTER the ConsolidationCandidate detection boundary.
    """
    candidate: ConsolidationCandidate
    quality_report: ConsolidationQualityReport
    evaluation_candles: List[Candle] = Field(..., description="Candles occurring AFTER candidate detection")
    configuration: ConsolidationLifecycleConfiguration
    
    model_config = {"frozen": True}

class ConsolidationLifecycleSnapshot(BaseModel):
    """
    Immutable representation of a consolidation's state at a specific point in time.
    
    IMPORTANT: Identity Principle
    Candidate identity is completely static. The candidate itself does not change.
    Instead, its lifecycle snapshots evolve sequentially over time:
    Candidate -> Snapshot 1 -> Snapshot 2 -> ... -> ENDED.
    """
    snapshot_id: str
    candidate_id: str
    quality_report_id: str
    parent_candidate_snapshot_version: int
    quality_report_version: int
    configuration_version: int
    lifecycle_rule_version: str
    lifecycle_algorithm_version: str
    
    symbol: str
    timeframe: str
    lifecycle_state: ConsolidationLifecycleState
    supporting_evidence: List[BaseLifecycleEvidence]
    
    generated_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate_id(cls, candidate_id: str, quality_report_id: str, state: str, config_hash: str) -> str:
        payload = f"{candidate_id}_{quality_report_id}_{state}_{config_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    model_config = {"frozen": True}
