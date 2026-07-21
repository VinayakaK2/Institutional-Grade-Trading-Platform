from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import RiskEvaluationReport

class PositionRiskMetadata(BaseModel):
    execution_duration_ms: int = Field(description="Total execution time in milliseconds")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution info")
    
    model_config = {"frozen": True}

class RiskEvaluationSnapshot(BaseModel):
    """
    Immutable snapshot containing the finalized risk evaluation.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the snapshot")
    context: PositionRiskEvaluationContext = Field(description="Execution context")
    report: RiskEvaluationReport = Field(description="Evaluation report containing evidence")
    metadata: PositionRiskMetadata = Field(description="Associated metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    model_config = {"frozen": True}
