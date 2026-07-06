from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class OBVCalculator(BaseCalculator):
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.OBV

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[IndicatorResult]:
        
        self._validate_candles(candles, 1)
        
        results = []
        
        obv = 0.0
        prev_close = None
        
        if previous_state:
            obv = previous_state.get("obv", 0.0)
            prev_close = previous_state.get("prev_close")
            
        for candle in candles:
            close = float(candle.close)
            volume = float(candle.volume)
            
            if prev_close is not None:
                if close > prev_close:
                    obv += volume
                elif close < prev_close:
                    obv -= volume
                    
            prev_close = close
            
            internal_state = {
                "obv": obv,
                "prev_close": prev_close
            }
            
            results.append(
                IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={},
                    value=obv,
                    internal_state=internal_state
                )
            )
            
        return results
