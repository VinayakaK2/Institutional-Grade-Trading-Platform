from pydantic import BaseModel
from backend.shared.snapshots.models import SnapshotReference

class PortfolioDecisionLineage(BaseModel):
    """
    Immutable lineage explicitly capturing the exact upstream snapshots 
    consumed to make this decision.
    """
    portfolio_state_snapshot: SnapshotReference
    portfolio_exposure_snapshot: SnapshotReference
    portfolio_correlation_snapshot: SnapshotReference
    risk_decision_snapshot: SnapshotReference
    candidate_position_snapshot: SnapshotReference

    model_config = {"frozen": True}
