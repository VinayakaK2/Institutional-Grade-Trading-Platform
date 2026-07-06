from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class MACDCalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        # MACDCalculator produces multiple types, but we'll use MACD as its primary identity
        return IndicatorType.MACD

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        fast_period = kwargs.get("fast_period", 12)
        slow_period = kwargs.get("slow_period", 26)
        signal_period = kwargs.get("signal_period", 9)
        
        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("MACD periods must be > 0")
        if fast_period >= slow_period:
            raise ValueError("MACD fast_period must be < slow_period")
            
        self._validate_candles(candles, slow_period + signal_period - 1)
        
        prices = self._extract_prices(candles, "close")
        results = []
        
        # Calculate EMA function helper
        def calc_emas(prices_list, period):
            sma_seed = sum(prices_list[:period]) / period
            multiplier = 2 / (period + 1)
            emas = [None] * (period - 1) + [sma_seed]
            current_ema = sma_seed
            for i in range(period, len(prices_list)):
                current_ema = (prices_list[i] - current_ema) * multiplier + current_ema
                emas.append(current_ema)
            return emas

        fast_emas = calc_emas(prices, fast_period)
        slow_emas = calc_emas(prices, slow_period)
        
        # Compute MACD Line (Fast EMA - Slow EMA)
        macd_line: List[Optional[float]] = []
        for i in range(len(prices)):
            if slow_emas[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(fast_emas[i] - slow_emas[i])
                
        # We need a list of valid MACD values to compute the Signal line
        valid_macd_start = slow_period - 1
        valid_macd_values = macd_line[valid_macd_start:]
        
        if len(valid_macd_values) < signal_period:
            return [] # Not enough data for signal
            
        signal_emas = calc_emas(valid_macd_values, signal_period)
        
        # Now assemble the results
        # The first valid signal (and thus full MACD set) is at index valid_macd_start + signal_period - 1
        params = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
        
        for i, signal_val in enumerate(signal_emas):
            if signal_val is None:
                continue
                
            candle_index = valid_macd_start + i
            candle = candles[candle_index]
            macd_val = macd_line[candle_index]
            hist_val = macd_val - signal_val
            
            base_kwargs = dict(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                parameters=params
            )
            
            results.append(IndicatorResult(indicator_type=IndicatorType.MACD, value=macd_val, **base_kwargs))
            results.append(IndicatorResult(indicator_type=IndicatorType.MACD_SIGNAL, value=signal_val, **base_kwargs))
            results.append(IndicatorResult(indicator_type=IndicatorType.MACD_HISTOGRAM, value=hist_val, **base_kwargs))
            
        return results
