from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class DecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    REJECTED = "REJECTED"

class DecisionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DecisionReason(BaseModel):
    """
    Structured machine-readable explanation of why a decision was made.
    """
    code: str
    severity: DecisionSeverity
    category: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}

class DecisionMetadata(BaseModel):
    """
    Institutional metadata capturing the operational aspects of the decision.
    """
    decision_id: str
    pipeline_version: str
    configuration_version: str
    engine_version: str
    rule_version: str
    execution_duration_ms: int
    decision_timestamp: str

    model_config = {"frozen": True}

class PortfolioDecision(BaseModel):
    """
    The final deterministic decision for the portfolio.
    """
    status: DecisionStatus
    reasons: List[DecisionReason] = Field(default_factory=list)
    metadata: DecisionMetadata

    model_config = {"frozen": True}
