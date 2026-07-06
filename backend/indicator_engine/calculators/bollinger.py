from typing import List, Dict, Any, Optional
import math
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class BollingerBandsCalculator(BaseCalculator):
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.BOLLINGER_BANDS

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[IndicatorResult]:
        
        period = kwargs.get("period", 20)
        std_dev_multiplier = float(kwargs.get("std_dev_multiplier", 2.0))
        
        if period <= 0:
            raise ValueError("Bollinger Bands period must be > 0")
            
        self._validate_candles(candles, period)
        
        prices = self._extract_prices(candles, "close")
        results = []
        
        for i in range(len(prices)):
            if i < period - 1:
                continue
                
            window = prices[i - period + 1 : i + 1]
            mean = sum(window) / period
            
            variance = sum((x - mean) ** 2 for x in window) / period
            std_dev = math.sqrt(variance)
            
            upper_band = mean + (std_dev_multiplier * std_dev)
            lower_band = mean - (std_dev_multiplier * std_dev)
            
            candle = candles[i]
            results.append(
                IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={"period": period, "std_dev_multiplier": std_dev_multiplier},
                    value=mean,  # middle band
                    outputs={
                        "upper_band": upper_band,
                        "lower_band": lower_band
                    }
                )
            )
            
        return results
