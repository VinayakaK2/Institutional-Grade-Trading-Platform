from typing import Dict, Any
from pydantic import BaseModel, Field

class ValidationRulesConfig(BaseModel):
    """
    Configuration for the Validation Rules Engine pipeline.
    Contains strictly infrastructure and pipeline parameters, not business thresholds.
    """
    fail_fast: bool = Field(default=False, description="Halt execution immediately on first rule failure")
    diagnostic_mode: bool = Field(default=False, description="Enable extensive diagnostic data collection")
    pipeline_version: str = Field(default="1.0.0", description="Version of the current validation pipeline configuration")
    logging_options: Dict[str, Any] = Field(default_factory=dict, description="Options for structured pipeline logging")

    model_config = {"frozen": True}
