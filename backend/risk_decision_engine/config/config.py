from pydantic import BaseModel, Field

class RiskDecisionConfig(BaseModel):
    """
    Configuration for the Risk Decision Engine.
    """
    pipeline_version: str = Field(default="1.0.0", description="Version of the pipeline to run")
    validation_enabled: bool = Field(default=True, description="Whether structural and consistency validation is enabled")
    fail_fast: bool = Field(default=False, description="If true, execution fails on the first pipeline stage error")
    metadata_enabled: bool = Field(default=True, description="Whether to gather execution metadata")
    
    model_config = {"frozen": True}
