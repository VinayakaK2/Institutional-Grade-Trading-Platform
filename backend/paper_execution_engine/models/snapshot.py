from typing import List
from pydantic import StrictStr, ConfigDict
from backend.shared.snapshots.models import BaseSnapshot

class PaperExecutionSnapshot(BaseSnapshot):
    """
    Immutable snapshot output representing the deterministic result of the Paper Execution Engine.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    
    engine_version: StrictStr
    snapshot_version: StrictStr
    pipeline_version: StrictStr
    configuration_hash: StrictStr
    snapshot_hash: StrictStr
    parent_snapshot_versions: List[StrictStr]
    business_fingerprint: StrictStr
