from typing import Dict, Any
from pydantic import BaseModel, Field

class PortfolioDecisionConfigurationSnapshot(BaseModel):
    """
    Deterministic snapshot of the configuration used during the pipeline execution.
    """
    configuration_hash: str
    dataset_version: str
    pipeline_version: str
    rule_version: str
    limits: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
