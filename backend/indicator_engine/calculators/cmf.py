from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class CMFCalculator(BaseCalculator):
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.CMF

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[IndicatorResult]:
        
        period = kwargs.get("period", 20)
        
        if period <= 0:
            raise ValueError("CMF period must be > 0")
            
        self._validate_candles(candles, 1)
        
        results = []
        
        mfv_window = []
        vol_window = []
        
        if previous_state:
            mfv_window = previous_state.get("mfv_window", [])
            vol_window = previous_state.get("vol_window", [])
            
        for candle in candles:
            high = float(candle.high)
            low = float(candle.low)
            close = float(candle.close)
            volume = float(candle.volume)
            
            if high == low:
                mfm = 0.0
            else:
                mfm = ((close - low) - (high - close)) / (high - low)
                
            mfv = mfm * volume
            
            mfv_window.append(mfv)
            vol_window.append(volume)
            
            if len(mfv_window) > period:
                mfv_window.pop(0)
            if len(vol_window) > period:
                vol_window.pop(0)
                
            # Need at least 'period' candles to output a valid CMF, but to be consistent 
            # with other sliding windows, we can output partial if we don't return None.
            # But usually it's None until period is reached.
            if len(mfv_window) == period:
                sum_vol = sum(vol_window)
                if sum_vol == 0:
                    cmf_val = 0.0
                else:
                    cmf_val = sum(mfv_window) / sum_vol
                    
                internal_state = {
                    "mfv_window": list(mfv_window),
                    "vol_window": list(vol_window)
                }
                
                results.append(
                    IndicatorResult(
                        symbol=candle.symbol,
                        timeframe=candle.timeframe,
                        dataset_version=dataset_version,
                        timestamp=candle.timestamp,
                        indicator_type=self.indicator_type,
                        parameters={"period": period},
                        value=cmf_val,
                        internal_state=internal_state
                    )
                )
            
        return results
