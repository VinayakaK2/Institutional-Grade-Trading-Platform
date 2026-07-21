from pydantic import BaseModel, Field
from typing import List
from backend.risk_decision_engine.models.evidence import (
    RiskThresholdEvidence, PortfolioDecisionEvidence, ExposureDecisionEvidence,
    SectorDecisionEvidence, CorrelationDecisionEvidence, DailyRiskDecisionEvidence,
    OpenRiskDecisionEvidence, FinalDecisionEvidence
)

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="True if context is structurally consistent")
    errors: List[str] = Field(default_factory=list, description="Validation errors if any")
    
    model_config = {"frozen": True}

class RiskDecisionReport(BaseModel):
    """
    Contains the final decision, reason, typed evidence, and metadata.
    """
    validation_status: ValidationResult = Field(description="Structural validation result")
    
    # Typed Evidence from individual stages
    risk_threshold_evidence: RiskThresholdEvidence = Field(description="Risk threshold decision")
    portfolio_constraint_evidence: PortfolioDecisionEvidence = Field(description="Portfolio constraint decision")
    position_exposure_evidence: ExposureDecisionEvidence = Field(description="Position exposure decision")
    sector_exposure_evidence: SectorDecisionEvidence = Field(description="Sector exposure decision")
    correlation_evidence: CorrelationDecisionEvidence = Field(description="Correlation decision")
    daily_risk_evidence: DailyRiskDecisionEvidence = Field(description="Daily risk decision")
    open_risk_evidence: OpenRiskDecisionEvidence = Field(description="Open risk decision")
    
    # Final aggregated evidence
    final_decision_evidence: FinalDecisionEvidence = Field(description="Final decision representation")
    
    configuration_version: str = Field(description="Configuration version used for decision")
    algorithm_version: str = Field(description="Algorithm version used")
    
    model_config = {"frozen": True}
