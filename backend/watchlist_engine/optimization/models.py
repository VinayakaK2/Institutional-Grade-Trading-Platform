"""
Optimization Engine Models
==========================

Models specific to Phase 6.5 Optimization Layer.
"""
from pydantic import BaseModel, ConfigDict


class OptimizationSummary(BaseModel):
    """
    Summary of the optimization applied during snapshot generation.
    Appended to WatchlistSnapshot metadata.
    """
    model_config = ConfigDict(frozen=True)

    total_candidates: int
    processed_candidates: int
    reused_candidates: int
    reuse_percentage: float
    
    incremental_enabled: bool
    parallel_enabled: bool
    worker_count: int
    batch_size: int
    
    optimization_version: str = "1.0.0"
    fingerprint_version: int = 1
