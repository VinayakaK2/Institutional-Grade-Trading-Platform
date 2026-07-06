from typing import List
from backend.market_data.models.candle import Candle
from backend.support_resistance_engine.models.zone import SwingPoint, SwingType
from backend.support_resistance_engine.contracts.engine import SwingDetectorContract

class SwingDetector(SwingDetectorContract):
    def __init__(self, lookback: int = 5, lookforward: int = 5):
        if lookback < 1 or lookforward < 1:
            raise ValueError("Lookback and lookforward must be at least 1")
        self.lookback = lookback
        self.lookforward = lookforward

    def detect_swings(self, candles: List[Candle], lookback: int = None, lookforward: int = None) -> List[SwingPoint]:
        lb = lookback if lookback is not None else self.lookback
        lf = lookforward if lookforward is not None else self.lookforward
        
        swings = []
        n = len(candles)
        
        for i in range(lb, n - lf):
            current_candle = candles[i]
            current_high = float(current_candle.high)
            current_low = float(current_candle.low)
            
            # Extract window
            window_start = i - lb
            window_end = i + lf
            
            # Check Swing High
            is_swing_high = True
            for j in range(window_start, window_end + 1):
                if j == i:
                    continue
                compare_high = float(candles[j].high)
                # If equal high, we take the earliest one (so if a previous candle is equal, we are NOT the swing high)
                # If a future candle is equal, we ARE the swing high (it won't be)
                if compare_high > current_high:
                    is_swing_high = False
                    break
                elif compare_high == current_high and j < i:
                    is_swing_high = False
                    break
                    
            if is_swing_high:
                swings.append(
                    SwingPoint(
                        type=SwingType.HIGH,
                        price=current_high,
                        timestamp=current_candle.timestamp,
                        candle_high=current_high,
                        candle_low=current_low,
                        candle_open=float(current_candle.open),
                        candle_close=float(current_candle.close)
                    )
                )
                
            # Check Swing Low
            is_swing_low = True
            for j in range(window_start, window_end + 1):
                if j == i:
                    continue
                compare_low = float(candles[j].low)
                if compare_low < current_low:
                    is_swing_low = False
                    break
                elif compare_low == current_low and j < i:
                    is_swing_low = False
                    break
                    
            if is_swing_low:
                swings.append(
                    SwingPoint(
                        type=SwingType.LOW,
                        price=current_low,
                        timestamp=current_candle.timestamp,
                        candle_high=current_high,
                        candle_low=current_low,
                        candle_open=float(current_candle.open),
                        candle_close=float(current_candle.close)
                    )
                )
                
        # Sort chronologically, just in case (though loop processes sequentially)
        swings.sort(key=lambda x: x.timestamp)
        return swings
