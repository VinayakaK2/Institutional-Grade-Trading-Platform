from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle

class RVOLClassification(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"

class VolumeEventType(str, Enum):
    EXPANSION = "expansion"
    CONTRACTION = "contraction"
    CLIMAX = "climax"
    DRY_VOLUME = "dry_volume"

class CandleClassification(str, Enum):
    BULLISH = "bullish_candle"
    BEARISH = "bearish_candle"
    NEUTRAL = "neutral_candle"

class VolumeAnalysisResult(BaseModel):
    """
    Result of Relative Volume (RVOL) analysis for a single candle.
    """
    model_config = ConfigDict(frozen=True)
    
    id: str
    symbol: SymbolReference
    timeframe: Timeframe
    dataset_version: str
    timestamp: datetime
    
    volume: float
    avg_volume: float
    rvol: float
    classification: RVOLClassification

class VolumeEvent(BaseModel):
    """
    A detected volume event (expansion, contraction, climax, dry volume).
    """
    model_config = ConfigDict(frozen=True)
    
    event_id: str
    symbol_id: str
    symbol: SymbolReference
    timeframe: Timeframe
    dataset_version: str
    timestamp: datetime
    
    event_type: VolumeEventType
    event_strength: float # typically the RVOL multiplier
    relative_volume: float
    
    candle_classification: CandleClassification
    trigger_candle: Candle
    
    metadata: Optional[Dict[str, Any]] = None
