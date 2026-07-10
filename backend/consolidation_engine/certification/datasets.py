import math
from datetime import datetime, timedelta, timezone
from typing import List

from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe

class SyntheticDataGenerator:
    """
    Level 1: Component Verification
    Generates deterministic OHLCV datasets for certification of production algorithms.
    These datasets exercise the REAL pipeline and algorithms by producing
    perfect mathematical shapes representing known market conditions.
    """
    
    @classmethod
    def get_symbol(cls) -> SymbolReference:
        return SymbolReference(
            symbol="TEST",
            exchange=ExchangeReference(
                code="TEST"
            )
        )
        
    @classmethod
    def generate_candles(
        cls, 
        pattern_type: str, 
        count: int = 100, 
        start_price: float = 100.0,
        start_time: datetime = None
    ) -> List[Candle]:
        """
        Generates deterministic candles based on a specific pattern.
        """
        if start_time is None:
            start_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
            
        candles = []
        symbol = cls.get_symbol()
        
        current_time = start_time
        base_price = start_price
        
        for i in range(count):
            open_p, high_p, low_p, close_p = base_price, base_price, base_price, base_price
            
            if pattern_type == "simple_consolidation":
                # Flat range, minor oscillation
                oscillation = math.sin(i) * 0.5
                open_p = base_price
                close_p = base_price + oscillation
                high_p = base_price + abs(oscillation) + 0.1
                low_p = base_price - abs(oscillation) - 0.1
                
            elif pattern_type == "no_consolidation":
                # Strong trend upwards
                base_price += 1.0
                open_p = base_price - 1.0
                close_p = base_price
                high_p = base_price + 0.5
                low_p = base_price - 1.5
                
            elif pattern_type == "broken_consolidation":
                if i < int(count * 0.8):
                    # Consolidating
                    oscillation = math.sin(i) * 0.5
                    open_p = base_price
                    close_p = base_price + oscillation
                    high_p = base_price + abs(oscillation) + 0.1
                    low_p = base_price - abs(oscillation) - 0.1
                else:
                    # Sudden violent breakout
                    base_price += 2.0
                    open_p = base_price - 2.0
                    close_p = base_price
                    high_p = base_price + 0.5
                    low_p = open_p - 0.5
            else:
                # Default flat
                pass
                
            candle = Candle(
                symbol=symbol,
                timeframe=Timeframe.H1,
                timestamp=current_time,
                open=round(open_p, 4),
                high=round(high_p, 4),
                low=round(low_p, 4),
                close=round(close_p, 4),
                volume=1000.0,
                is_completed=True
            )
            candles.append(candle)
            
            # Increment time
            current_time += timedelta(hours=1)
            
        return candles
