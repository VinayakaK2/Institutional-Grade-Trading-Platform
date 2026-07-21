from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.position_risk_engine.config.config import PositionRiskConfig

class PositionRiskEvaluationContext(BaseModel):
    """
    Immutable context passed through the Position Risk Evaluation Pipeline.
    Strictly excludes position_size, cash_balance, and broker_state.
    """
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    trade_decision_snapshot_version: str = Field(description="Parent Trade Decision Snapshot ID")
    entry_price: float = Field(description="Planned entry price")
    initial_stop_loss: float = Field(description="Planned initial stop loss")
    instrument_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the instrument (e.g., pip size)")
    configuration: PositionRiskConfig = Field(description="Infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    model_config = {"frozen": True}
