from typing import List, Optional
from pydantic import StrictStr, ConfigDict
from backend.shared.snapshots.models import BaseSnapshot
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.models.events import FillEvent

class PaperFillSnapshot(BaseSnapshot):
    """
    The immutable persisted output of the Fill Simulation Engine.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_version: StrictStr
    
    # Parent References
    parent_paper_order_snapshot_version: StrictStr
    
    # Core state
    fill_state: FillState
    fill_events: List[FillEvent]
    total_filled_quantity: int
    remaining_quantity: int
    average_fill_price: Optional[float]
    
    business_fingerprint: StrictStr
    snapshot_hash: StrictStr
