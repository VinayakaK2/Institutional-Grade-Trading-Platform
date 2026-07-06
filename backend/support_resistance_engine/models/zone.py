from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class SwingType(str, Enum):
    HIGH = "high"
    LOW = "low"

class ZoneType(str, Enum):
    SUPPORT = "support"
    RESISTANCE = "resistance"

class SwingPoint(BaseModel):
    """
    Represents a detected swing point in the market.
    Immutable.
    """
    model_config = ConfigDict(frozen=True)
    
    type: SwingType
    price: float
    timestamp: datetime
    # We store the candle details to derive the zone width
    candle_high: float
    candle_low: float
    candle_open: float
    candle_close: float
    
class ZoneStrength(BaseModel):
    """
    Deterministic structural strength metrics of a zone.
    """
    model_config = ConfigDict(frozen=False)
    
    touch_count: int = 0
    rejection_count: int = 0
    zone_age_candles: int = 0
    last_interaction_timestamp: Optional[datetime] = None

    @property
    def confidence_score(self) -> float:
        """
        Confidence Score Normalization:
        The score is bounded between 0.0 and 1.0 (or theoretically higher if unbounded, 
        but designed to scale predictably). 
        Calculated primarily based on:
        - Touch count (each touch adds weight)
        - Rejection count (strong rejections add more weight)
        - Zone age (older zones may decay or strengthen depending on touches)
        """
        # Simple placeholder calculation for structural confidence
        # E.g. base 0.1 + (touches * 0.1) + (rejections * 0.2), capped at 1.0
        score = 0.1 + (self.touch_count * 0.1) + (self.rejection_count * 0.2)
        return min(1.0, score)

class Zone(BaseModel):
    """
    Represents a Support or Resistance zone.
    """
    model_config = ConfigDict(frozen=False)
    
    # Identifier (usually a hash or UUID)
    id: str
    
    symbol: SymbolReference
    timeframe: Timeframe
    dataset_version: str
    
    zone_type: ZoneType
    center: float
    upper_boundary: float
    lower_boundary: float
    
    created_at: datetime
    source_swing_point: SwingPoint
    
    strength: ZoneStrength
    is_active: bool = True
