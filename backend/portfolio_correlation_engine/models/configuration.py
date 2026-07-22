from typing import Dict, Any
from pydantic import BaseModel, Field

class PortfolioCorrelationConfigurationSnapshot(BaseModel):
    """
    Immutable configuration snapshot defining correlation settings and thresholds.
    """
    configuration_version: str = "1.0"
    configuration_hash: str = Field(description="Deterministic hash of the configuration")
    active_correlation_settings: Dict[str, Any] = Field(default_factory=dict)
    active_threshold_definitions: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
