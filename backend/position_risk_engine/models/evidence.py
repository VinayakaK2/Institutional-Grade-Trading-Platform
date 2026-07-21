from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any

class RiskEvidenceBase(BaseModel):
    calculation_method: str = Field(description="Description of how the metric was calculated")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Calculation timestamp")
    source_snapshot_id: str = Field(description="Parent TradeDecisionSnapshot ID for traceability")
    metric_version: str = Field(default="1.0.0", description="Version of the metric calculation")
    engine_version: str = Field(default="1.0.0", description="Version of the position risk engine")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or standard version fields")
    
    model_config = {"frozen": True}

class EntryEvidence(RiskEvidenceBase):
    entry_price: float = Field(description="Validated entry price")

class StopLossEvidence(RiskEvidenceBase):
    stop_loss: float = Field(description="Validated stop loss price")

class DistanceEvidence(RiskEvidenceBase):
    entry_price: float = Field(description="Base entry price")
    stop_loss: float = Field(description="Base stop loss")
    risk_distance: float = Field(description="Absolute numerical distance between entry and stop loss")

class AbsoluteRiskEvidence(RiskEvidenceBase):
    entry_price: float = Field(description="Base entry price")
    stop_loss: float = Field(description="Base stop loss")
    risk_distance: float = Field(description="Risk distance")
    absolute_risk: float = Field(description="Absolute monetary risk distance")

class PercentageRiskEvidence(RiskEvidenceBase):
    entry_price: float = Field(description="Base entry price")
    stop_loss: float = Field(description="Base stop loss")
    percentage_risk: float = Field(description="Percentage distance risk (e.g., 0.05 for 5%)")

class PerUnitRiskEvidence(RiskEvidenceBase):
    entry_price: float = Field(description="Base entry price")
    stop_loss: float = Field(description="Base stop loss")
    risk_per_unit: float = Field(description="Currency risk per unit traded")
