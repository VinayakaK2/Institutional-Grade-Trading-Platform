from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from backend.position_sizing_engine.models.evidence import (
    CapitalAllocationEvidence, MaximumRiskEvidence, 
    RawPositionSizeEvidence, RoundLotEvidence, RemainingCashEvidence
)

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation error messages, if any")
    
    model_config = {"frozen": True}

class PositionSizingReport(BaseModel):
    """
    Immutable aggregation of all evidence and validation results.
    """
    validation_status: ValidationResult = Field(description="Validation results")
    capital_allocation_evidence: Optional[CapitalAllocationEvidence] = Field(default=None, description="Capital allocation evidence")
    maximum_risk_evidence: Optional[MaximumRiskEvidence] = Field(default=None, description="Maximum risk evidence")
    raw_position_size_evidence: Optional[RawPositionSizeEvidence] = Field(default=None, description="Raw position size evidence")
    round_lot_evidence: Optional[RoundLotEvidence] = Field(default=None, description="Round lot evidence")
    remaining_cash_evidence: Optional[RemainingCashEvidence] = Field(default=None, description="Remaining cash evidence")
    configuration_version: str = Field(description="Version of configuration used")
    algorithm_version: str = Field(description="Version of the algorithms used")
    supporting_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    
    model_config = {"frozen": True}
