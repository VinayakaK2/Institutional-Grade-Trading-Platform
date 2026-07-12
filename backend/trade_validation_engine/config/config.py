from pydantic import BaseModel, Field

class TradeValidationConfig(BaseModel):
    """
    Configuration for the Trade Validation Engine.
    Contains infrastructure and orchestration settings only.
    No business logic thresholds.
    """
    fail_fast: bool = Field(
        default=True, 
        description="If True, pipeline halts on the first validation failure."
    )
    timeout_ms: int = Field(
        default=5000, 
        description="Timeout for validation execution in milliseconds."
    )
    max_retries: int = Field(
        default=3, 
        description="Maximum number of retries for repository operations."
    )
    
    model_config = {"frozen": True}
