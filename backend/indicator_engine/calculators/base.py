from typing import List
from backend.market_data.models.candle import Candle
from backend.indicator_engine.contracts.calculator import IndicatorCalculatorContract

class BaseCalculator(IndicatorCalculatorContract):
    """
    Base class for calculators to provide common utility functions and validations.
    """
    
    def _validate_candles(self, candles: List[Candle], min_required: int) -> None:
        """
        Validates the candles list.
        """
        if not candles:
            raise ValueError(f"Cannot calculate {self.indicator_type.value}: candles list is empty.")
        if len(candles) < min_required:
            raise ValueError(f"Cannot calculate {self.indicator_type.value}: requires at least {min_required} candles, got {len(candles)}.")
            
    def _extract_prices(self, candles: List[Candle], price_type: str = "close") -> List[float]:
        """
        Extracts a specific price array from candles.
        """
        return [float(getattr(c, price_type)) for c in candles]
