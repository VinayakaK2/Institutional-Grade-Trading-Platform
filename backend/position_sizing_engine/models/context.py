from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.position_sizing_engine.config.config import PositionSizingConfig
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot

class ParentRiskSnapshotReference(BaseModel):
    snapshot_id: str = Field(description="Deterministic SHA-256 ID of the parent risk snapshot")
    snapshot_version: str = Field(description="Version of the parent risk snapshot")
    dataset_version: str = Field(description="Underlying dataset version")
    configuration_hash: str = Field(description="Hash of the parent configuration")
    
    model_config = {"frozen": True}

class PositionSizingContext(BaseModel):
    """
    Immutable context passed through the Position Sizing Evaluation Pipeline.
    Strictly excludes mutable state and portfolio logic.
    """
    parent_risk_snapshot: ParentRiskSnapshotReference = Field(description="Strongly typed reference to parent risk snapshot")
    risk_evaluation_snapshot: RiskEvaluationSnapshot = Field(description="Full immutable risk evaluation snapshot")
    available_capital: float = Field(description="Available capital for this evaluation")
    allocation_configuration: Dict[str, Any] = Field(description="Allocation configuration (e.g. max_risk_pct, allocation_pct)")
    instrument_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the instrument (e.g., pip size, lot policies)")
    configuration: PositionSizingConfig = Field(description="Infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    model_config = {"frozen": True}
