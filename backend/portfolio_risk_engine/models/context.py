from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.portfolio_risk_engine.config.config import PortfolioRiskConfig
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot

class ParentSnapshotReferences(BaseModel):
    risk_snapshot_id: str = Field(description="Deterministic ID of the parent risk snapshot")
    risk_snapshot_version: str = Field(description="Version of the parent risk snapshot")
    sizing_snapshot_id: str = Field(description="Deterministic ID of the parent sizing snapshot")
    sizing_snapshot_version: str = Field(description="Version of the parent sizing snapshot")
    dataset_version: str = Field(description="Underlying dataset version")
    configuration_hash: str = Field(description="Hash of the parent configuration")
    
    model_config = {"frozen": True}

class PortfolioRiskContext(BaseModel):
    """
    Immutable context passed through the Portfolio Risk Evaluation Pipeline.
    Strictly excludes mutable state.
    """
    parent_snapshots: ParentSnapshotReferences = Field(description="Strongly typed reference to parent snapshots")
    risk_evaluation_snapshot: RiskEvaluationSnapshot = Field(description="Full immutable risk evaluation snapshot")
    position_sizing_snapshot: PositionSizingSnapshot = Field(description="Full immutable position sizing snapshot")
    configuration: PortfolioRiskConfig = Field(description="Infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    model_config = {"frozen": True}
