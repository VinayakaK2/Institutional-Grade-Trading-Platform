from pydantic import BaseModel
from typing import Optional

from backend.shared.snapshots.models import SnapshotReference

class ParentSnapshotReferences(BaseModel):
    """
    Consolidated lineage object pointing to the parent snapshots.
    """
    portfolio_state_snapshot: SnapshotReference
    portfolio_exposure_snapshot: SnapshotReference
    candidate_position_snapshot: SnapshotReference
    risk_decision_snapshot: SnapshotReference
    
    model_config = {"frozen": True}
