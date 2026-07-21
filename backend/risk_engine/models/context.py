from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.risk_engine.config.config import RiskEngineConfig

class RiskExecutionContext(BaseModel):
    """
    Immutable context passed through the Risk Pipeline.
    Strictly excludes business attributes like stop loss, entry price, or position size.
    """
    symbol: str = Field(description="Target symbol for the underlying trade decision")
    timeframe: str = Field(description="Target timeframe for the underlying trade decision")
    dataset_version: int = Field(description="Version of the dataset used")
    parent_trade_decision_snapshot_version: str = Field(description="Snapshot ID of the parent TradeDecisionSnapshot")
    configuration: RiskEngineConfig = Field(description="Infrastructure configuration for the Risk Engine")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    model_config = {"frozen": True}
