from typing import Optional
from pydantic import BaseModel, Field
from backend.trade_validation_engine.optimization.config.config import OptimizationConfig

class OptimizationStatistics(BaseModel):
    """
    Immutable model tracking optimization metrics.
    """
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses executed")
    reused_validations: int = Field(default=0, description="Number of validations perfectly reused")
    executed_validations: int = Field(default=0, description="Number of validations newly computed")
    
    worker_count: int = Field(default=0, description="Max concurrent workers actually utilized")
    batch_count: int = Field(default=0, description="Number of execution batches processed")
    
    fingerprint_time_ms: int = Field(default=0, description="Time spent building fingerprints")
    cache_lookup_time_ms: int = Field(default=0, description="Time spent querying the cache repository")
    parallel_execution_time_ms: int = Field(default=0, description="Time spent physically computing misses")
    merge_time_ms: int = Field(default=0, description="Time spent sorting and merging results")
    persistence_time_ms: int = Field(default=0, description="Time spent saving execution results")
    total_time_ms: int = Field(default=0, description="End-to-end processing time")

    model_config = {"frozen": True}

class CacheResolution(BaseModel):
    """
    Immutable object representing a cache lookup result.
    """
    cache_hit: bool = Field(description="True if found in cache")
    fingerprint: str = Field(description="Business fingerprint used for lookup")
    snapshot_reference: Optional[str] = Field(default=None, description="The snapshot ID if cache_hit is True")
    cache_reason: str = Field(description="Reason for cache hit/miss")

    model_config = {"frozen": True}

class OptimizationSnapshot(BaseModel):
    """
    Immutable aggregate root representing a completed optimization run.
    """
    optimization_id: str = Field(description="Deterministic SHA-256 ID of the optimization run")
    business_fingerprint: str = Field(description="Fingerprint of the validation context")
    optimization_engine_version: str = Field(description="Version of the optimization engine")
    
    configuration: OptimizationConfig = Field(description="Immutable configuration used during execution")
    runtime_statistics: OptimizationStatistics = Field(description="Execution performance metrics")
    
    source_trade_decision_snapshot_id: str = Field(description="Reference to the final TradeDecisionSnapshot produced")

    model_config = {"frozen": True}
