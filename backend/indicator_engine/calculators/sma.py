from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class SMACalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.SMA

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        period = kwargs.get("period", 14)
        if period <= 0:
            raise ValueError("SMA period must be > 0")
            
        self._validate_candles(candles, period)
        
        prices = self._extract_prices(candles, "close")
        results = []
        
        # We start emitting results from index (period - 1)
        # Because we need `period` candles to form the first SMA
        sum_window = sum(prices[:period-1])
        
        for i in range(period - 1, len(prices)):
            sum_window += prices[i]
            sma_val = sum_window / period
            
            candle = candles[i]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=sma_val
            ))
            
            # Remove the oldest element from the window sum for the next iteration
            sum_window -= prices[i - (period - 1)]
            
        return results

class VolumeSMACalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VOL_SMA

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        period = kwargs.get("period", 20)
        if period <= 0:
            raise ValueError("Volume SMA period must be > 0")
            
        self._validate_candles(candles, period)
        
        volumes = self._extract_prices(candles, "volume")
        results = []
        
        sum_window = sum(volumes[:period-1])
        
        for i in range(period - 1, len(volumes)):
            sum_window += volumes[i]
            sma_val = sum_window / period
            
            candle = candles[i]
            results.append(IndicatorResult(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                indicator_type=self.indicator_type,
                parameters={"period": period},
                value=sma_val
            ))
            sum_window -= volumes[i - (period - 1)]
            
        return results
