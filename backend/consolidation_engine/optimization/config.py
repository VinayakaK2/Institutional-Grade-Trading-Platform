from pydantic import BaseModel, Field

class ConsolidationOptimizationConfiguration(BaseModel):
    """Configuration for Consolidation Optimization Engine."""
    config_version: int = Field(default=1)
    
    batch_size: int = Field(default=100, description="Size of batches for processing.")
    max_concurrency: int = Field(default=10, description="Maximum number of parallel workers.")
    fingerprint_version: str = Field(default="1.0", description="Version of the fingerprint algorithm.")
    
    model_config = {"frozen": True}
