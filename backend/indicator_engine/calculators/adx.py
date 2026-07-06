from typing import List, Dict, Any, Optional
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.calculators.base import BaseCalculator

class ADXCalculator(BaseCalculator):
    
    @property
    def indicator_type(self) -> IndicatorType:
        return IndicatorType.ADX

    def calculate(self, candles: List[Candle], dataset_version: str, previous_state: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[IndicatorResult]:
        period = kwargs.get("period", 14)
        if period <= 0:
            raise ValueError("ADX period must be > 0")
            
        # We need enough data to calculate smoothed values. Wilder's ADX usually needs at least 2*period candles.
        self._validate_candles(candles, 2 * period)
        
        results = []
        
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []
        
        for i in range(1, len(candles)):
            curr = candles[i]
            prev = candles[i - 1]
            
            high = float(curr.high)
            low = float(curr.low)
            prev_high = float(prev.high)
            prev_low = float(prev.low)
            prev_close = float(prev.close)
            
            # True Range
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
            
            # Directional Movement
            up_move = high - prev_high
            down_move = prev_low - low
            
            if up_move > down_move and up_move > 0:
                plus_dm_list.append(up_move)
            else:
                plus_dm_list.append(0.0)
                
            if down_move > up_move and down_move > 0:
                minus_dm_list.append(down_move)
            else:
                minus_dm_list.append(0.0)
                
        # Initial smoothed values
        smoothed_tr = sum(tr_list[:period])
        smoothed_plus_dm = sum(plus_dm_list[:period])
        smoothed_minus_dm = sum(minus_dm_list[:period])
        
        dx_list = []
        # Calculate DX starting from index `period` (which is candle index `period`)
        for i in range(period, len(tr_list)):
            tr = tr_list[i]
            plus_dm = plus_dm_list[i]
            minus_dm = minus_dm_list[i]
            
            # Wilder's Smoothing: new = old - (old/period) + current
            smoothed_tr = smoothed_tr - (smoothed_tr / period) + tr
            smoothed_plus_dm = smoothed_plus_dm - (smoothed_plus_dm / period) + plus_dm
            smoothed_minus_dm = smoothed_minus_dm - (smoothed_minus_dm / period) + minus_dm
            
            di_plus = 100 * (smoothed_plus_dm / smoothed_tr) if smoothed_tr > 0 else 0.0
            di_minus = 100 * (smoothed_minus_dm / smoothed_tr) if smoothed_tr > 0 else 0.0
            
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus) if (di_plus + di_minus) > 0 else 0.0
            dx_list.append((dx, di_plus, di_minus))
            
        # Initial ADX is the SMA of the first `period` DX values
        if len(dx_list) < period:
            return []
            
        adx = sum(d[0] for d in dx_list[:period]) / period
        
        # Start emitting results
        # The first ADX is computed at index `period - 1` of the dx_list
        # dx_list[0] corresponds to tr_list[period], which corresponds to candles[period + 1]
        # Therefore, dx_list[period - 1] corresponds to candles[period + period]
        
        params = {"period": period}
        
        def emit_result(candle, adx_val, di_p, di_m):
            base_kwargs = dict(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                dataset_version=dataset_version,
                timestamp=candle.timestamp,
                parameters=params
            )
            results.append(IndicatorResult(indicator_type=IndicatorType.ADX, value=adx_val, **base_kwargs))
            results.append(IndicatorResult(indicator_type=IndicatorType.DI_PLUS, value=di_p, **base_kwargs))
            results.append(IndicatorResult(indicator_type=IndicatorType.DI_MINUS, value=di_m, **base_kwargs))
            
        first_candle_idx = 2 * period
        emit_result(
            candles[first_candle_idx],
            adx,
            dx_list[period - 1][1],
            dx_list[period - 1][2]
        )
        
        # Subsequent ADX values
        for i in range(period, len(dx_list)):
            dx, di_p, di_m = dx_list[i]
            adx = (adx * (period - 1) + dx) / period
            emit_result(candles[first_candle_idx + i - period + 1], adx, di_p, di_m)
            
        return results
