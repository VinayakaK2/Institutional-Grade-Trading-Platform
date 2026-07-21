from pydantic import BaseModel, Field

class PortfolioRiskConfig(BaseModel):
    """
    Configuration for the Portfolio Risk Validation Engine.
    Contains only infrastructure settings.
    """
    pipeline_version: str = Field(default="1.0.0", description="Version of the portfolio risk pipeline")
    validation_enabled: bool = Field(default=True, description="Enable structural and consistency validation")
    fail_fast: bool = Field(default=True, description="Halt execution on first validation or pipeline failure")
    metadata_enabled: bool = Field(default=True, description="Include execution metadata in the generated snapshots")
    
    model_config = {"frozen": True}
