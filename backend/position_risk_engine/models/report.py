from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from backend.position_risk_engine.models.evidence import (
    EntryEvidence, StopLossEvidence, DistanceEvidence, 
    AbsoluteRiskEvidence, PercentageRiskEvidence, PerUnitRiskEvidence
)

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation error messages, if any")
    
    model_config = {"frozen": True}

class RiskEvaluationReport(BaseModel):
    """
    Immutable aggregation of all evidence and validation results.
    """
    validation_status: ValidationResult = Field(description="Validation results")
    entry_evidence: Optional[EntryEvidence] = Field(default=None, description="Entry evidence")
    stop_loss_evidence: Optional[StopLossEvidence] = Field(default=None, description="Stop loss evidence")
    distance_evidence: Optional[DistanceEvidence] = Field(default=None, description="Distance evidence")
    absolute_risk_evidence: Optional[AbsoluteRiskEvidence] = Field(default=None, description="Absolute risk evidence")
    percentage_risk_evidence: Optional[PercentageRiskEvidence] = Field(default=None, description="Percentage risk evidence")
    per_unit_risk_evidence: Optional[PerUnitRiskEvidence] = Field(default=None, description="Per unit risk evidence")
    configuration_version: str = Field(description="Version of configuration used")
    algorithm_version: str = Field(description="Version of the algorithms used")
    supporting_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    
    model_config = {"frozen": True}
