from typing import List, Tuple
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.contracts.contracts import IBoundaryDetectionStrategy
from backend.consolidation_engine.exceptions import InvalidCandleDataError

class RangeDetector:
    """Orchestrates boundary detection using an injected strategy."""
    
    def __init__(self, boundary_strategy: IBoundaryDetectionStrategy):
        self._strategy = boundary_strategy
        
    def detect_range(self, candles: List[Candle]) -> Tuple[float, float, float]:
        """
        Uses the provided strategy to detect range boundaries.
        Returns (upper_boundary, lower_boundary, midpoint).
        """
        if not candles:
            raise InvalidCandleDataError("Cannot detect range from empty candle series.")
        return self._strategy.detect_boundaries(candles)
