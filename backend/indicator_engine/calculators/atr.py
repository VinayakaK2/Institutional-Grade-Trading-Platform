from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class ATRCalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.ATR

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        period = kwargs.get("period", 14)
        if period <= 0:
            raise ValueError("ATR period must be > 0")
            
        self._validate_candles(candles, period + 1)
        
        results = []
        true_ranges = []
        
        # Calculate True Range for all candles starting from index 1
        for i in range(1, len(candles)):
            curr = candles[i]
            prev = candles[i - 1]
            
            high = float(curr.high)
            low = float(curr.low)
            prev_close = float(prev.close)
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
            
        # First ATR is a simple average of the first `period` true ranges
        if len(true_ranges) < period:
            return []
            
        current_atr = sum(true_ranges[:period]) / period
        
        results.append(IndicatorResult(
            symbol=candles[period].symbol,
            timeframe=candles[period].timeframe,
            dataset_version=dataset_version,
            timestamp=candles[period].timestamp,
            indicator_type=self.indicator_type,
            parameters={"period": period},
            value=current_atr
        ))
        
        # Subsequent ATR values use smoothing
        for i in range(period, len(true_ranges)):
            tr = true_ranges[i]
            current_atr = (current_atr * (period - 1) + tr) / period
            
            candle = candles[i + 1]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=current_atr
            ))
            
        return results
