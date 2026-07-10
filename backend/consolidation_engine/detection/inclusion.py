from backend.market_data.models.candle import Candle
from backend.consolidation_engine.contracts.contracts import ICandleContainmentStrategy
from backend.consolidation_engine.exceptions import InvalidCandleDataError

class CandleInclusionValidator:
    """Orchestrates inclusion validation using an injected strategy."""
    
    def __init__(self, containment_strategy: ICandleContainmentStrategy):
        self._strategy = containment_strategy
        
    def validate_inclusion(self, candle: Candle, upper_boundary: float, lower_boundary: float) -> bool:
        """
        Returns True if the candle is contained according to the injected strategy.
        """
        if candle is None:
            raise InvalidCandleDataError("Cannot validate inclusion for None candle.")
        return self._strategy.is_contained(candle, upper_boundary, lower_boundary)
