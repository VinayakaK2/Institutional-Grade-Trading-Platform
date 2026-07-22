from pydantic import BaseModel, Field

class PortfolioConfiguration(BaseModel):
    """
    Purely infrastructure configuration for the Portfolio Engine.
    No business rules belong here.
    """
    fail_fast: bool = Field(default=True, description="Whether to fail immediately on first error")
    pipeline_version: str = Field(default="1.0", description="Version of the portfolio pipeline")
    validation_enabled: bool = Field(default=True, description="Whether structural and consistency validation is enabled")
    metadata_enabled: bool = Field(default=True, description="Whether to collect execution metadata")
    
    model_config = {"frozen": True}
