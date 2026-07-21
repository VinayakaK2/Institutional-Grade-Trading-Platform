from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class BusinessFingerprint(BaseModel):
    """
    Deterministically hashed value of all business-affecting inputs.
    Must include every factor that could change the pipeline output.
    """
    fingerprint_hash: str = Field(description="SHA-256 hash of the business inputs")
    dataset_version: str = Field(description="Version of the dataset used")
    algorithm_versions: Dict[str, str] = Field(description="Versions of all algorithms (evaluation, sizing, etc.)")
    rule_versions: Dict[str, str] = Field(description="Versions of rules applied")
    strategy_version: str = Field(description="Version of the trading strategy")
    parent_snapshot_id: str = Field(description="ID of the parent snapshot/request")
    risk_percentage: float = Field(description="Configured risk percentage")
    position_sizing_config: Dict[str, Any] = Field(description="Position sizing configuration parameters")
    portfolio_config: Dict[str, Any] = Field(description="Portfolio constraints configuration")
    decision_config: Dict[str, Any] = Field(description="Decision thresholds configuration")
    exchange_config: Optional[Dict[str, Any]] = Field(default=None, description="Exchange config if business affecting")
    
    model_config = {"frozen": True}
