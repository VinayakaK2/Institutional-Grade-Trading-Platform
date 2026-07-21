from pydantic import BaseModel, Field
from typing import Dict, Any, List
from enum import Enum

class StageStatus(str, Enum):
    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"

class DecisionType(str, Enum):
    """
    Final decision for the trade.
    Precedence: REJECTED > REDUCED > APPROVED
    """
    APPROVED = "APPROVED"
    REDUCED = "REDUCED"
    REJECTED = "REJECTED"

class DecisionEvidenceBase(BaseModel):
    """
    Abstract base for decision evidence from any single stage.
    """
    metric_id: str = Field(description="Deterministic ID for this evidence")
    stage_name: str = Field(default="Unknown", description="Name of the stage generating this evidence")
    status: StageStatus = Field(description="PASS or FAIL status of the evaluation")
    calculation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the evaluation logic")
    
    model_config = {"frozen": True}

class RiskThresholdEvidence(DecisionEvidenceBase):
    pass

class PortfolioDecisionEvidence(DecisionEvidenceBase):
    pass

class ExposureDecisionEvidence(DecisionEvidenceBase):
    pass

class SectorDecisionEvidence(DecisionEvidenceBase):
    pass

class CorrelationDecisionEvidence(DecisionEvidenceBase):
    pass

class DailyRiskDecisionEvidence(DecisionEvidenceBase):
    pass

class OpenRiskDecisionEvidence(DecisionEvidenceBase):
    pass

class DecisionExplanation(BaseModel):
    decision: DecisionType = Field(description="The final computed decision")
    primary_reason: str = Field(description="Textual explanation for the primary driver of this decision")
    contributing_evidence: List[str] = Field(default_factory=list, description="List of IDs or names of evidence objects that contributed to the decision")
    
    model_config = {"frozen": True}

class FinalDecisionEvidence(BaseModel):
    metric_id: str = Field(description="Deterministic ID for the final evidence")
    decision: DecisionType = Field(description="The final computed decision")
    reason: DecisionExplanation = Field(description="Detailed reason for the decision")
    triggered_rules: List[str] = Field(default_factory=list, description="Rules that contributed to REDUCED/REJECTED state")
    timestamp: str = Field(description="Execution timestamp")
    algorithm_version: str = Field(description="Algorithm version")
    
    model_config = {"frozen": True}
