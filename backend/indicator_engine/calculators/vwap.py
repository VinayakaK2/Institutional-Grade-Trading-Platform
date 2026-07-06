from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class VWAPCalculator(BaseCalculator):
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.VWAP

    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[IndicatorResult]:
        
        self._validate_candles(candles, 1)
        
        session_identifiers = kwargs.get("session_identifiers")
        if not session_identifiers or len(session_identifiers) != len(candles):
            raise ValueError("VWAP calculation requires 'session_identifiers' list matching the length of candles.")
            
        results = []
        
        cumulative_volume = 0.0
        cumulative_pv = 0.0
        current_session = None
        
        if previous_state:
            cumulative_volume = previous_state.get("cumulative_volume", 0.0)
            cumulative_pv = previous_state.get("cumulative_pv", 0.0)
            current_session = previous_state.get("current_session")
            
        for i, candle in enumerate(candles):
            session = session_identifiers[i]
            
            # Reset on new session
            if session != current_session:
                cumulative_volume = 0.0
                cumulative_pv = 0.0
                current_session = session
                
            high = float(candle.high)
            low = float(candle.low)
            close = float(candle.close)
            volume = float(candle.volume)
            
            typical_price = (high + low + close) / 3.0
            
            cumulative_volume += volume
            cumulative_pv += volume * typical_price
            
            vwap_value = cumulative_pv / cumulative_volume if cumulative_volume > 0 else typical_price
            
            internal_state = {
                "cumulative_volume": cumulative_volume,
                "cumulative_pv": cumulative_pv,
                "current_session": current_session
            }
            
            results.append(
                IndicatorResult(
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    dataset_version=dataset_version,
                    timestamp=candle.timestamp,
                    indicator_type=self.indicator_type,
                    parameters={},
                    value=vwap_value,
                    internal_state=internal_state
                )
            )
            
        return results

