from pydantic import BaseModel, Field
from typing import Dict, Any

class PortfolioOptimizationConfiguration(BaseModel):
    """
    Configuration parameters for the Portfolio Optimization Engine.
    """
    configuration_hash: str
    pipeline_version: str
    dataset_version: str
    optimization_targets: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}
