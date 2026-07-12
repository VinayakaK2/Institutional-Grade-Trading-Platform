import hashlib
# no-op
from pydantic import BaseModel, ConfigDict, Field

from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot

class OptimizationContext(BaseModel):
    """
    Context that orchestrates how the optimization engine executes.
    """
    cache_enabled: bool = Field(default=True, description="Whether to use the optimization repository cache")
    reuse_enabled: bool = Field(default=True, description="Whether to skip re-execution if cache hits")
    batch_size: int = Field(default=50, description="Size of batches for parallel processing")
    max_parallelism: int = Field(default=4, description="Maximum number of parallel workers")

    model_config = ConfigDict(frozen=True)

class BusinessFingerprint(BaseModel):
    """
    Deterministic fingerprint identifying the core business components.
    Used for caching and reuse.
    """
    candidate_id: str
    dataset_version: int
    config_hash: str
    detection_algorithm_version: str
    quality_algorithm_version: str
    lifecycle_algorithm_version: str
    
    @property
    def fingerprint_hash(self) -> str:
        payload = (
            f"{self.candidate_id}_{self.dataset_version}_{self.config_hash}_"
            f"{self.detection_algorithm_version}_{self.quality_algorithm_version}_"
            f"{self.lifecycle_algorithm_version}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    model_config = ConfigDict(frozen=True)

class OptimizationRuntimeStatistics(BaseModel):
    """
    Tracks runtime statistics separate from business objects.
    """
    candidates_processed: int = 0
    candidates_reused: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    batch_count: int = 0
    execution_duration_ms: float = 0.0

    model_config = ConfigDict(frozen=True)

class OptimizationMetadata(BaseModel):
    """
    Metadata about the optimization process itself.
    """
    optimization_engine_version: str
    optimization_timestamp: float
    
    model_config = ConfigDict(frozen=True)

class OptimizationSnapshot(BaseModel):
    """
    The immutable output of the optimization engine.
    Wraps the business output (Lifecycle Snapshot) with optimization metadata.
    """
    snapshot_id: str
    business_fingerprint: BusinessFingerprint
    lifecycle_snapshot: LiquidityGrabLifecycleSnapshot
    metadata: OptimizationMetadata
    runtime_statistics: OptimizationRuntimeStatistics

    model_config = ConfigDict(frozen=True)
