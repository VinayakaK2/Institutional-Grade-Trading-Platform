from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator
from backend.indicator_engine.calculators.atr import ATRCalculator

class SuperTrendCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self._atr_calc = ATRCalculator()

    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.SUPERTREND

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[IndicatorResult]:
        
        atr_period = kwargs.get("atr_period", 10)
        multiplier = float(kwargs.get("multiplier", 3.0))
        
        if atr_period <= 0:
            raise ValueError("SuperTrend atr_period must be > 0")
            
        self._validate_candles(candles, atr_period)
        
        # Calculate ATR using the existing calculator
        atr_results = self._atr_calc.calculate(
            candles, 
            dataset_version, 
            previous_state=previous_state.get("atr_state") if previous_state else None,
            period=atr_period
        )
        
        # We need a quick lookup of ATR values by timestamp
        atr_map = {res.timestamp: res for res in atr_results}
        
        results = []
        
        prev_final_upper = 0.0
        prev_final_lower = 0.0
        prev_close = 0.0
        prev_trend = 1
        
        if previous_state:
            prev_final_upper = previous_state.get("final_upper", 0.0)
            prev_final_lower = previous_state.get("final_lower", 0.0)
            prev_close = previous_state.get("prev_close", 0.0)
            prev_trend = previous_state.get("trend", 1)
            
        for i, candle in enumerate(candles):
            if candle.timestamp not in atr_map:
                # We skip candles that don't have enough history for ATR
                # Keep updating prev_close just in case
                prev_close = float(candle.close)
                continue
                
            atr_val = atr_map[candle.timestamp].value
            atr_internal_state = atr_map[candle.timestamp].internal_state
            
            high = float(candle.high)
            low = float(candle.low)
            close = float(candle.close)
            
            hl2 = (high + low) / 2.0
            basic_upper = hl2 + (multiplier * atr_val)
            basic_lower = hl2 - (multiplier * atr_val)
            
            # Initial state setup
            if prev_final_upper == 0.0:
                prev_final_upper = basic_upper
            if prev_final_lower == 0.0:
                prev_final_lower = basic_lower
            if prev_close == 0.0:
                prev_close = close
                
            if basic_upper < prev_final_upper or prev_close > prev_final_upper:
                final_upper = basic_upper
            else:
                final_upper = prev_final_upper
                
            if basic_lower > prev_final_lower or prev_close < prev_final_lower:
                final_lower = basic_lower
            else:
                final_lower = prev_final_lower
                
            if prev_trend == 1 and close < final_lower:
                trend = -1
            elif prev_trend == -1 and close > final_upper:
                trend = 1
            else:
                trend = prev_trend
                
            active_band = final_lower if trend == 1 else final_upper
            
            internal_state = {
                "final_upper": final_upper,
                "final_lower": final_lower,
                "prev_close": close,
                "trend": trend,
                "atr_state": atr_internal_state
            }
            
            results.append(
                IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={"atr_period": atr_period, "multiplier": multiplier},
                    value=active_band,
                    outputs={
                        "upper_band": final_upper,
                        "lower_band": final_lower,
                        "trend_direction": float(trend)
                    },
                    internal_state=internal_state
                )
            )
            
            prev_final_upper = final_upper
            prev_final_lower = final_lower
            prev_close = close
            prev_trend = trend
            
        return results
