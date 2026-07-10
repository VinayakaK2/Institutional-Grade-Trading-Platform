
import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.detection.inclusion import CandleInclusionValidator
from backend.consolidation_engine.exceptions import InvalidCandleDataError
from backend.consolidation_engine.contracts.contracts import ICandleContainmentStrategy

class MockContainmentStrategy(ICandleContainmentStrategy):
    def is_contained(self, candle, upper, lower):
        return candle.close <= upper and candle.close >= lower

def test_inclusion_validator_success():
    validator = CandleInclusionValidator(MockContainmentStrategy())
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    c = Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=datetime.now(timezone.utc), open=1, high=10, low=1, close=5, volume=100)
    assert validator.validate_inclusion(c, 10.0, 1.0) is True
    assert validator.validate_inclusion(c, 4.0, 1.0) is False

def test_inclusion_validator_none():
    validator = CandleInclusionValidator(MockContainmentStrategy())
    with pytest.raises(InvalidCandleDataError):
        validator.validate_inclusion(None, 10.0, 1.0)  # type: ignore
