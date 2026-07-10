import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class BusinessFingerprint(BaseModel):
    """
    Deterministic hash representing exact business inputs.
    Excludes runtime metadata.
    """
    fingerprint_version: str
    
    # Business-impacting properties
    candidate_id: str
    candidate_version: int
    quality_report_version: int
    lifecycle_snapshot_version: int
    configuration_hash: str
    algorithm_versions: str
    
    @property
    def digest(self) -> str:
        """
        Computes SHA-256 using canonical serialization (sorted keys).
        """
        data = self.model_dump(mode="json")
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    model_config = {"frozen": True}

class OptimizationBusinessStatistics(BaseModel):
    total_candidates: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    model_config = {"frozen": True}

class OptimizationRuntimeStatistics(BaseModel):
    execution_time_ms: float = 0.0
    batch_count: int = 0
    worker_count: int = 0
    
    model_config = {"frozen": True}

class ConsolidationOptimizationSnapshot(BaseModel):
    snapshot_id: str
    parent_snapshot_id: Optional[str] = None
    
    business_fingerprint: str
    fingerprint_version: str
    optimization_algorithm_version: str
    
    business_statistics: OptimizationBusinessStatistics
    runtime_statistics: OptimizationRuntimeStatistics
    
    configuration_version: int
    generated_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate_id(cls, fingerprint: str, timestamp: datetime) -> str:
        payload = f"{fingerprint}_{timestamp.isoformat()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    model_config = {"frozen": True}

class ConsolidationProcessingRequest(BaseModel):
    """Encapsulates a request for consolidation processing."""
    request_id: str
    fingerprint: BusinessFingerprint
    payload: Any = Field(description="The actual data/context required for processing.")
    
    model_config = {"frozen": True}

class ConsolidationProcessingResult(BaseModel):
    """Encapsulates the result of a processed consolidation request."""
    request_id: str
    fingerprint: str
    cached: bool
    result_payload: Any = Field(description="The finalized domain object (e.g., LifecycleSnapshot).")
    
    model_config = {"frozen": True}
