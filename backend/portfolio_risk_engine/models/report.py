from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from backend.portfolio_risk_engine.models.evidence import (
    PortfolioExposureEvidence, PositionExposureEvidence,
    SectorExposureEvidence, CorrelationEvidence,
    DailyRiskEvidence, OpenRiskEvidence
)

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation error messages, if any")
    
    model_config = {"frozen": True}

class PortfolioRiskReport(BaseModel):
    """
    Immutable aggregation of all evidence and validation results.
    Does NOT approve or reject the trade, purely validates limits.
    """
    validation_status: ValidationResult = Field(description="Validation results from constraints")
    portfolio_exposure_evidence: Optional[PortfolioExposureEvidence] = Field(default=None, description="Portfolio exposure validation evidence")
    position_exposure_evidence: Optional[PositionExposureEvidence] = Field(default=None, description="Single position exposure validation evidence")
    sector_exposure_evidence: Optional[SectorExposureEvidence] = Field(default=None, description="Sector exposure validation evidence")
    correlation_evidence: Optional[CorrelationEvidence] = Field(default=None, description="Correlation validation evidence")
    daily_risk_evidence: Optional[DailyRiskEvidence] = Field(default=None, description="Daily risk limit validation evidence")
    open_risk_evidence: Optional[OpenRiskEvidence] = Field(default=None, description="Open risk limit validation evidence")
    
    configuration_version: str = Field(description="Version of configuration used")
    algorithm_version: str = Field(description="Version of the algorithms used")
    supporting_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    
    model_config = {"frozen": True}
