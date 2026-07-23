from pydantic import StrictStr, ConfigDict
from backend.shared.snapshots.models import BaseSnapshot
from backend.paper_execution_quality_engine.models.execution_quality import ExecutionQualityReport

class PaperExecutionQualitySnapshot(BaseSnapshot):
    """
    The immutable persisted output of the Execution Quality Engine.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_version: StrictStr
    parent_fill_snapshot_version: StrictStr
    
    execution_quality_report: ExecutionQualityReport
    
    business_fingerprint: StrictStr
    snapshot_hash: StrictStr
