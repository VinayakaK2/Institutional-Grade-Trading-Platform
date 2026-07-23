from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class OptimizationRuntimeStatistics(BaseModel):
    """
    Operational metrics for the optimization process.
    Must not affect business logic.
    """
    model_config = ConfigDict(frozen=True)

    cache_hits: int = Field(default=0, ge=0)
    cache_misses: int = Field(default=0, ge=0)
    reused_snapshots: int = Field(default=0, ge=0)
    recomputed_snapshots: int = Field(default=0, ge=0)
    recomputed_snapshots: int = Field(default=0, ge=0)
    parallel_workers: int = Field(default=1, ge=1)
    batch_duration_ms: float = Field(default=0.0, ge=0.0)
    average_snapshot_duration_ms: float = Field(default=0.0, ge=0.0)


class PaperExecutionOptimizationSnapshot(BaseModel):
    """
    Immutable optimization snapshot for a paper execution result.
    Does not embed the full business snapshot, only references its ID.
    Maintains exact business fingerprint and a canonical hash.
    """
    model_config = ConfigDict(frozen=True)

    optimization_fingerprint: str = Field(
        description="Deterministic fingerprint representing the optimization conditions."
    )
    business_fingerprint: str = Field(
        description="Must remain identical to the parent PaperExecutionSnapshot."
    )
    canonical_hash: str = Field(
        description="Unique deterministic hash of this entire optimization snapshot."
    )
    snapshot_version: str = Field(
        description="The ID/version reference of the underlying PaperExecutionSnapshot."
    )
    optimization_summary: OptimizationRuntimeStatistics = Field(
        description="Runtime metrics for this specific snapshot generation."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary optimization metadata. Must not participate in business hashing."
    )
    
    def is_business_equivalent(self, other: "PaperExecutionOptimizationSnapshot") -> bool:
        """
        Determines strictly if this snapshot is equivalent to another one from a business perspective.
        Matches on business_fingerprint AND snapshot_version to prevent schema evolution collisions.
        """
        return (
            self.business_fingerprint == other.business_fingerprint and 
            self.snapshot_version == other.snapshot_version
        )
