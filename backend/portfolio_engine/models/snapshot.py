from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioSnapshot(BaseModel):
    """
    The canonical immutable entity resulting from pipeline execution.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 identifier")
    parent_snapshot_references: ParentSnapshotReferences = Field(description="Lineage parent snapshots")
    dataset_version: str = Field(description="Version of the market dataset")
    pipeline_version: str = Field(description="Version of the portfolio pipeline")
    configuration_hash: str = Field(description="Hash of the business-impacting configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"frozen": True}
