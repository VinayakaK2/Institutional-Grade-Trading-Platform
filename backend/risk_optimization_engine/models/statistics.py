from pydantic import BaseModel, Field
from datetime import datetime, timezone

class OptimizationStatistics(BaseModel):
    """
    Immutable record of cache usage and processing statistics.
    """
    batch_id: str = Field(description="Unique ID for this batch execution")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")
    total_snapshots: int = Field(default=0, description="Total number of snapshots processed")
    reuse_percentage: float = Field(default=0.0, description="Percentage of snapshots reused from cache")
    processing_time_ms: float = Field(default=0.0, description="Total processing time in milliseconds")
    parallelism: bool = Field(default=True, description="Whether parallel execution was used")
    worker_count: int = Field(default=1, description="Number of workers used")
    batch_count: int = Field(default=1, description="Number of batches processed")
    
    model_config = {"frozen": True}
