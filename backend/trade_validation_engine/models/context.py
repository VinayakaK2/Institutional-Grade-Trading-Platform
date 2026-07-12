from typing import Dict, Any
from pydantic import BaseModel, Field

from backend.trade_validation_engine.config.config import TradeValidationConfig

class TradeValidationExecutionContext(BaseModel):
    """
    Immutable execution context for Trade Validation.
    Contains only execution metadata and required parent snapshot versions.
    No business state.
    """
    symbol: str = Field(description="The target symbol")
    timeframe: str = Field(description="The target timeframe")
    dataset_version: int = Field(description="The dataset version used")
    
    parent_watchlist_snapshot_version: int = Field(description="Parent Watchlist Snapshot version")
    parent_trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    parent_consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    parent_liquidity_grab_snapshot_version: int = Field(description="Parent Liquidity Grab Snapshot version")
    
    configuration: TradeValidationConfig = Field(description="Infrastructure configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution metadata")
    
    model_config = {"frozen": True}
