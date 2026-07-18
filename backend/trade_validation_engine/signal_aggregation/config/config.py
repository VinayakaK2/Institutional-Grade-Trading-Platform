from pydantic import BaseModel, Field

class SignalAggregationConfig(BaseModel):
    """
    Infrastructure configuration for the Signal Aggregation Engine.
    Contains no business logic or thresholds.
    """
    fail_fast: bool = Field(default=False, description="If True, halt aggregation on first failure")
    timeout_ms: int = Field(default=5000, description="Pipeline timeout in ms")
    max_retries: int = Field(default=3, description="Maximum repository retries")
    
    model_config = {"frozen": True}
