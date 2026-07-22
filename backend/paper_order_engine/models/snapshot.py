from typing import Dict, Any
from pydantic import StrictStr, ConfigDict
from backend.shared.snapshots.models import BaseSnapshot
from backend.paper_order_engine.models.order import OrderState

class PaperOrderSnapshot(BaseSnapshot):
    """
    The immutable persisted output of the Order Simulation Engine.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_version: StrictStr
    
    # Parent References
    parent_portfolio_decision_snapshot_version: StrictStr
    parent_paper_execution_snapshot_version: StrictStr
    
    # Core state
    order_state: OrderState
    
    order_metadata: Dict[str, Any]
    business_fingerprint: StrictStr
    snapshot_hash: StrictStr
