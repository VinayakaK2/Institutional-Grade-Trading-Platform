from typing import Dict, Any
from pydantic import BaseModel, Field

class TradeDecisionConfig(BaseModel):
    """
    Infrastructure configuration for the Trade Decision Engine.
    """
    pipeline_version: str = Field(default="1.0.0", description="Version of the pipeline configuration")
    fail_fast: bool = Field(default=False, description="Whether to stop execution on the first rejected stage")
    diagnostic_mode: bool = Field(default=False, description="Enable extensive diagnostics metadata collection")
    logging_options: Dict[str, Any] = Field(default_factory=dict, description="Logging configuration options")
    
    model_config = {"frozen": True}

TRADE_DECISION_ALGORITHM_VERSION = "1.0.0"
