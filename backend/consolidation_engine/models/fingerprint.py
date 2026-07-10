import hashlib
import json
from pydantic import BaseModel, Field

class BusinessFingerprint(BaseModel):
    """
    Deterministic hash model representing purely business-impacting inputs.
    
    MUST INCLUDE:
    - Parent Dataset Version
    - Parent Trend Snapshot Version
    - Pipeline Version
    - Configuration Hash
    
    MUST NEVER INCLUDE:
    - UUIDs, IDs, Timestamps
    - Runtime/Debug/Audit metadata
    """
    fingerprint_algorithm_version: int = Field(default=1, description="Version of the fingerprint algorithm.")
    parent_dataset_version: int = Field(..., description="The snapshot version of the market dataset")
    parent_trend_snapshot_version: int = Field(..., description="The snapshot version of the detected trends")
    pipeline_version: str = Field(..., description="Overall pipeline version (e.g. 1.0)")
    engine_version: str = Field(default="1.0", description="Consolidation Engine version")
    config_hash: str = Field(..., description="Hash of the ConsolidationConfig parameters")
    
    def compute_hash(self) -> str:
        """Computes a deterministic SHA-256 hash of the business inputs."""
        payload = {
            "fav": self.fingerprint_algorithm_version,
            "pdv": self.parent_dataset_version,
            "ptv": self.parent_trend_snapshot_version,
            "pv": self.pipeline_version,
            "ev": self.engine_version,
            "ch": self.config_hash
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
    
    model_config = {"frozen": True}
