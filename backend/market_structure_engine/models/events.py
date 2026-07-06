from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.models.zone import SwingPoint

class EventType(str, Enum):
    BOS = "BOS"      # Break of Structure
    CHOCH = "CHOCH"  # Change of Character

class EventSignal(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"

class StructureEvent(BaseModel):
    """
    Represents a structural event (BoS or ChoCH).
    """
    model_config = ConfigDict(frozen=True)
    
    id: str
    type: EventType
    signal: EventSignal
    
    # The candle that confirmed the break
    trigger_candle: Candle
    
    # The structural swing point that was broken
    reference_swing: SwingPoint
    
    timestamp: datetime
