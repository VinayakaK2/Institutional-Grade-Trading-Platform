from typing import Dict, Any
from pydantic import StrictStr, ConfigDict
from backend.shared.snapshots.models import BaseSnapshot
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus, ExecutionSummary, ExecutionTimeline

class PaperExecutionSnapshot(BaseSnapshot):
    """
    The immutable persisted output of the Execution Result Engine.
    Aggregates upstream models to establish final deterministic outcome.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_version: StrictStr
    
    # Lineage Links
    parent_portfolio_decision_snapshot_version: StrictStr
    parent_order_snapshot_version: StrictStr
    parent_fill_snapshot_version: StrictStr
    parent_execution_quality_snapshot_version: StrictStr
    
    execution_status: ExecutionStatus
    execution_summary: ExecutionSummary
    execution_timeline: ExecutionTimeline
    
    business_fingerprint: StrictStr
    canonical_hash: StrictStr
    
    metadata: Dict[str, Any]
