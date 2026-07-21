from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any

class PortfolioEvidenceBase(BaseModel):
    metric_id: str = Field(description="Unique ID for the metric")
    metric_version: str = Field(default="1.0.0", description="Version of the metric calculation")
    source_snapshot_id: str = Field(description="Parent Snapshot ID for traceability (typically Sizing Snapshot)")
    calculation_metadata: Dict[str, Any] = Field(description="Description of how the metric was calculated")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Calculation timestamp")
    is_valid: bool = Field(description="True if projected risk is within limits")
    
    model_config = {"frozen": True}

class PortfolioExposureEvidence(PortfolioEvidenceBase):
    current_portfolio_risk: float = Field(description="Total existing portfolio risk")
    new_position_risk: float = Field(description="Risk of the new position")
    projected_portfolio_risk: float = Field(description="Portfolio risk if new position is added")
    max_portfolio_risk_limit: float = Field(description="Maximum allowed portfolio risk limit")

class PositionExposureEvidence(PortfolioEvidenceBase):
    symbol: str = Field(description="Asset symbol")
    current_position_exposure: float = Field(description="Current exposure to this symbol")
    new_position_exposure: float = Field(description="Exposure of the new trade")
    projected_position_exposure: float = Field(description="Projected total exposure to this symbol")
    max_position_exposure_limit: float = Field(description="Maximum allowed exposure for a single symbol")

class SectorExposureEvidence(PortfolioEvidenceBase):
    sector: str = Field(description="Sector of the asset")
    current_sector_exposure: float = Field(description="Current exposure to this sector")
    new_position_exposure: float = Field(description="Exposure of the new trade")
    projected_sector_exposure: float = Field(description="Projected total exposure to this sector")
    max_sector_exposure_limit: float = Field(description="Maximum allowed exposure for a single sector")

class CorrelationEvidence(PortfolioEvidenceBase):
    symbol: str = Field(description="Asset symbol")
    highly_correlated_assets: Dict[str, float] = Field(description="Map of asset -> correlation coefficient (above threshold)")
    max_correlation_limit: float = Field(description="Maximum allowed correlation threshold")

class DailyRiskEvidence(PortfolioEvidenceBase):
    current_daily_loss: float = Field(description="Current accumulated daily loss")
    new_position_risk: float = Field(description="Risk of the new position")
    projected_daily_risk: float = Field(description="Projected total daily risk")
    max_daily_loss_limit: float = Field(description="Maximum allowed daily loss")

class OpenRiskEvidence(PortfolioEvidenceBase):
    current_open_risk: float = Field(description="Current total open risk")
    new_position_risk: float = Field(description="Risk of the new position")
    projected_open_risk: float = Field(description="Projected total open risk")
    max_open_risk_limit: float = Field(description="Maximum allowed open risk")
