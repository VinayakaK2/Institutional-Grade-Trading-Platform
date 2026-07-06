from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe

class IndicatorType(str, Enum):
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    MACD_SIGNAL = "macd_signal"
    MACD_HISTOGRAM = "macd_hist"
    ADX = "adx"
    DI_PLUS = "di_plus"
    DI_MINUS = "di_minus"
    ATR = "atr"
    VOL_SMA = "vol_sma"
    VWAP = "vwap"
    BOLLINGER_BANDS = "bollinger_bands"
    SUPERTREND = "supertrend"
    OBV = "obv"
    CMF = "cmf"

class IndicatorResult(BaseModel):
    """
    Domain model for a single computed indicator value.
    Immutable to guarantee deterministic behavior.
    """
    model_config = ConfigDict(frozen=True)
    
    symbol: SymbolReference
    timeframe: Timeframe
    dataset_version: str
    timestamp: datetime
    
    indicator_type: IndicatorType
    parameters: Dict[str, Any]
    
    value: float
    outputs: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    internal_state: Optional[Dict[str, Any]] = None
    
    def get_param_key(self) -> str:
        """
        Returns a canonical string representation of the parameters
        for efficient database indexing and querying.
        E.g., {"period": 14} -> "period=14"
        """
        sorted_keys = sorted(self.parameters.keys())
        return ",".join([f"{k}={self.parameters[k]}" for k in sorted_keys])

class IndicatorQueryFilters(BaseModel):
    """
    Filters for retrieving indicator values.
    """
    model_config = ConfigDict(frozen=True)
    
    symbol: SymbolReference
    timeframe: Timeframe
    dataset_version: str
    indicator_type: IndicatorType
    parameters: Dict[str, Any]
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = None

    def get_param_key(self) -> str:
        sorted_keys = sorted(self.parameters.keys())
        return ",".join([f"{k}={self.parameters[k]}" for k in sorted_keys])
