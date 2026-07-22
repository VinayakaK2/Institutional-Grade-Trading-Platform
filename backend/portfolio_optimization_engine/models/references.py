from pydantic import BaseModel
from backend.shared.snapshots.models import SnapshotReference

class ParentSnapshotReferences(BaseModel):
    """
    Consolidated lineage object pointing to the parent snapshots.
    """
    portfolio_state_snapshot: SnapshotReference
    portfolio_exposure_snapshot: SnapshotReference
    portfolio_correlation_snapshot: SnapshotReference
    portfolio_decision_snapshot: SnapshotReference
    
    model_config = {"frozen": True}
