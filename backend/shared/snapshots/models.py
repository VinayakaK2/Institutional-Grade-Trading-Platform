from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SnapshotReference(BaseModel):
    """
    Detailed reference to a parent snapshot supporting deterministic replay and auditing.
    """
    snapshot_id: str
    snapshot_version: Optional[str] = None
    business_fingerprint: Optional[str] = None
    dataset_version: Optional[str] = None
    
    model_config = {"frozen": True}

class BaseSnapshot(BaseModel):
    """
    Foundational snapshot base class providing universal attributes.
    """
    snapshot_id: str
    schema_version: str
    dataset_version: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
