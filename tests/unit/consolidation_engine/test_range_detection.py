
import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.detection.range import RangeDetector
from backend.consolidation_engine.exceptions import InvalidCandleDataError
from backend.consolidation_engine.contracts.contracts import IBoundaryDetectionStrategy

class MockBoundaryStrategy(IBoundaryDetectionStrategy):
    def detect_boundaries(self, candles):
        return (100.0, 50.0, 75.0)
    
    def get_minimum_candles(self):
        return 3

def test_range_detector_success():
    detector = RangeDetector(MockBoundaryStrategy())
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    c1 = Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=datetime.now(timezone.utc), open=1, high=2, low=1, close=1, volume=100)
    upper, lower, mid = detector.detect_range([c1])
    assert upper == 100.0
    assert lower == 50.0
    assert mid == 75.0

def test_range_detector_empty_candles():
    detector = RangeDetector(MockBoundaryStrategy())
    with pytest.raises(InvalidCandleDataError):
        detector.detect_range([])
