from pydantic import BaseModel, ConfigDict

class OptimizationConfig(BaseModel):
    """Configuration settings for the Paper Execution Optimization Engine."""
    model_config = ConfigDict(frozen=True)
    
    caching_enabled: bool = True
    concurrency_limit: int = 10
    fail_fast: bool = True
    configuration_hash: str = "default_hash"

# Fixed version string for fingerprinting
OPTIMIZATION_ENGINE_VERSION = "1.0.0"
