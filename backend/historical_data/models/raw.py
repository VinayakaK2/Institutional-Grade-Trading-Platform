"""
Historical Data Models - Raw Provider Data
"""
from typing import Any, Dict
from pydantic import BaseModel, Field
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference

class RawCandle(BaseModel):
    """
    Immutable representation of raw data returned by a provider.
    This serves as the exact footprint of what was downloaded, before any
    normalization or validation takes place.
    """
    provider: str
    symbol: SymbolReference
    timeframe: Timeframe
    raw_timestamp: Any = Field(..., description="The exact timestamp string/int from the provider")
    raw_open: Any
    raw_high: Any
    raw_low: Any
    raw_close: Any
    raw_volume: Any
    
    extra_data: Dict[str, Any] = Field(default_factory=dict, description="Any additional metadata provided (e.g. trades, vwap)")

