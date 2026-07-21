from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any
from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.report import RiskDecisionReport

class DecisionType(str, Enum):
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    REJECTED = "REJECTED"

class RiskDecisionMetadata(BaseModel):
    execution_duration_ms: float = Field(description="Time taken to execute the decision engine")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution info")

class RiskDecisionSnapshot(BaseModel):
    """
    Pure immutable representation of the final risk decision.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the snapshot")
    context: RiskDecisionContext = Field(description="The context used to generate the decision")
    report: RiskDecisionReport = Field(description="The complete report and typed evidence")
    metadata: RiskDecisionMetadata = Field(description="Execution metadata")
    
    model_config = {"frozen": True}
