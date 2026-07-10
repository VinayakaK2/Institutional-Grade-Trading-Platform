from pydantic import BaseModel, Field

class TrendOptimizationConfig(BaseModel):
    """Configuration for the Trend Optimization Engine."""
    
    is_incremental_enabled: bool = Field(
        default=True,
        description="Whether incremental processing (reusing cached symbols) is enabled."
    )
    
    is_cache_enabled: bool = Field(
        default=True,
        description="Whether writing to and reading from the optimization cache is enabled."
    )
    
    is_parallel_enabled: bool = Field(
        default=True,
        description="Whether to execute the pipeline in parallel."
    )
    
    worker_count: int = Field(
        default=4,
        ge=1,
        description="Number of parallel workers (or batch concurrency limit)."
    )
    
    batch_size: int = Field(
        default=50,
        ge=1,
        description="Size of symbol chunks for parallel execution."
    )
    
    configuration_hash: str = Field(
        default="1.0.0",
        description="Hash representing this configuration version."
    )

    model_config = {"frozen": True}
