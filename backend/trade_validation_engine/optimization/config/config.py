from pydantic import BaseModel, Field

OPTIMIZATION_ENGINE_VERSION = "1.0.0"

class OptimizationConfig(BaseModel):
    """
    Infrastructure configuration for the Trade Validation Optimization Engine.
    """
    batch_size: int = Field(default=100, description="Size of asynchronous execution batches")
    concurrency_limit: int = Field(default=10, description="Max concurrent executions (Semaphore limit)")
    caching_enabled: bool = Field(default=True, description="Whether to reuse cached validation results")
    fail_fast: bool = Field(default=True, description="Whether to cancel remaining parallel tasks on first generic failure")
    
    model_config = {"frozen": True}
