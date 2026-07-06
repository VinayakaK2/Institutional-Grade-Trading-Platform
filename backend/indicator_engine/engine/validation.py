from typing import List
from backend.market_data.models.candle import Candle

class IndicatorValidationEngine:
    """
    Validates candle series before they are passed to calculators.
    """
    
    @staticmethod
    def validate(candles: List[Candle]) -> None:
        if not candles:
            raise ValueError("Empty candle series provided.")
            
        seen_timestamps = set()
        
        for i, c in enumerate(candles):
            if c.timestamp in seen_timestamps:
                raise ValueError(f"Duplicate timestamp detected: {c.timestamp}")
            seen_timestamps.add(c.timestamp)
            
            # Null values check (assuming required fields cannot be None due to Pydantic, 
            # but we explicitly check for float('nan') or invalid math states)
            if any(val != val for val in (c.open, c.high, c.low, c.close, c.volume)):
                raise ValueError(f"Null or NaN values detected at timestamp: {c.timestamp}")
            
            if i > 0:
                prev_c = candles[i - 1]
                if c.timestamp <= prev_c.timestamp:
                    raise ValueError(f"Candles are not in strictly ascending chronological order at timestamp: {c.timestamp}")
                if c.symbol != prev_c.symbol:
                    raise ValueError("Candles series contains mixed symbols.")
                if c.timeframe != prev_c.timeframe:
                    raise ValueError("Candles series contains mixed timeframes.")
