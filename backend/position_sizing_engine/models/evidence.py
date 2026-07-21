from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any

class SizingEvidenceBase(BaseModel):
    metric_id: str = Field(description="Unique ID for the metric")
    metric_version: str = Field(default="1.0.0", description="Version of the metric calculation")
    source_snapshot_id: str = Field(description="Parent RiskEvaluationSnapshot ID for traceability")
    calculation_metadata: Dict[str, Any] = Field(description="Description of how the metric was calculated")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Calculation timestamp")
    
    model_config = {"frozen": True}

class CapitalAllocationEvidence(SizingEvidenceBase):
    available_capital: float = Field(description="Available capital before allocation")
    allocation_percentage: float = Field(description="Percentage of available capital to allocate")
    allocated_capital: float = Field(description="Capital allocated for this trade")

class MaximumRiskEvidence(SizingEvidenceBase):
    allocated_capital: float = Field(description="Allocated capital")
    max_risk_percentage: float = Field(description="Max risk percentage allowed on allocated capital")
    max_risk_amount: float = Field(description="Max risk amount allowed")

class RawPositionSizeEvidence(SizingEvidenceBase):
    max_risk_amount: float = Field(description="Max risk amount")
    risk_per_unit: float = Field(description="Currency risk per unit traded")
    raw_position_size: float = Field(description="Theoretical raw position size before rounding")

class RoundLotEvidence(SizingEvidenceBase):
    raw_position_size: float = Field(description="Theoretical raw position size")
    rounded_position_size: float = Field(description="Actual position size after rounding")
    rounding_policy: str = Field(description="Name of the rounding policy applied")

class RemainingCashEvidence(SizingEvidenceBase):
    allocated_capital: float = Field(description="Capital initially allocated")
    position_cost: float = Field(description="Cost to open position (size * price)")
    remaining_cash: float = Field(description="Remaining cash after theoretical position creation")
