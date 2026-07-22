from pydantic import BaseModel, Field

class ParentSnapshotReferences(BaseModel):
    """
    Encapsulates all parent snapshot lineage references.
    """
    risk_snapshot_version: str = Field(description="ID of the parent Risk Decision/Optimization snapshot")
    
    model_config = {"frozen": True}
