from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.report import PositionSizingReport

class PositionSizingMetadata(BaseModel):
    execution_duration_ms: int = Field(description="Total execution time in milliseconds")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution info")
    
    model_config = {"frozen": True}

class PositionSizingSnapshot(BaseModel):
    """
    Immutable snapshot containing the finalized position sizing evaluation.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the snapshot")
    context: PositionSizingContext = Field(description="Execution context")
    report: PositionSizingReport = Field(description="Sizing report containing evidence")
    metadata: PositionSizingMetadata = Field(description="Associated metadata (excluded from deterministic hashing)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    
    model_config = {"frozen": True}
