"""
Candle Model
"""
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference

class Candle(BaseModel):
    """Universal OHLCV data structure."""
    symbol: SymbolReference
    timeframe: Timeframe
    timestamp: datetime = Field(..., description="Start time of the candle (UTC)")
    
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    is_completed: bool = Field(default=True, description="False if this is a live, unfinished candle")

    @model_validator(mode='after')
    def validate_candle_mathematics(self) -> 'Candle':
        """Ensures that the candle data is mathematically possible."""
        # 1. No negative prices
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            raise ValueError(f"Prices cannot be negative. Got O:{self.open}, H:{self.high}, L:{self.low}, C:{self.close}")
            
        # 2. No negative volume
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative. Got {self.volume}")
            
        # 3. High must be the absolute highest point
        if self.high < self.open or self.high < self.close or self.high < self.low:
            raise ValueError(f"High ({self.high}) must be >= Open, Close, and Low")
            
        # 4. Low must be the absolute lowest point
        if self.low > self.open or self.low > self.close or self.low > self.high:
            raise ValueError(f"Low ({self.low}) must be <= Open, Close, and High")
            
        return self
