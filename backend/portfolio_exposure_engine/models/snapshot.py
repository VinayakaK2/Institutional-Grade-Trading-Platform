from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.portfolio_exposure_engine.models.exposure_models import PortfolioExposureAnalysis
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioExposureSnapshot(BaseModel):
    """
    The canonical immutable entity resulting from pipeline execution.
    Contains PortfolioExposureAnalysis, infrastructure metadata, lineage, and the hash.
    """
    snapshot_id: str = Field(description="Deterministic SHA-256 fingerprint")
    exposure_analysis: PortfolioExposureAnalysis = Field(description="The calculated exposure analysis")
    parent_snapshot_references: ParentSnapshotReferences = Field(description="Lineage tracking")
    dataset_version: str = Field(description="Version of the market dataset")
    pipeline_version: str = Field(description="Version of the portfolio pipeline")
    configuration_hash: str = Field(description="Hash of the business configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"frozen": True}
