import pytest
from datetime import datetime, timezone, timedelta
from typing import List, Tuple
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.consolidation_engine.engine.engine import ConsolidationDetectionEngine
from backend.consolidation_engine.models.fingerprint import BusinessFingerprint
from backend.consolidation_engine.contracts.contracts import (
    IBoundaryDetectionStrategy,
    ICandleContainmentStrategy,
    IWindowRequirement
)

class DummyWindowRequirement(IWindowRequirement):
    def get_minimum_candles(self) -> int:
        return 2

class DummyBoundaryStrategy(IBoundaryDetectionStrategy):
    def detect_boundaries(self, candles: List[Candle]) -> Tuple[float, float, float]:
        return (10.0, 1.0, 5.5)
    def get_minimum_candles(self):
        return 2

class DummyContainmentStrategy(ICandleContainmentStrategy):
    def is_contained(self, candle, upper, lower):
        return lower <= candle.close <= upper

@pytest.fixture
def base_fingerprint():
    return BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )

def test_engine_no_candles(base_fingerprint):
    engine = ConsolidationDetectionEngine(DummyWindowRequirement(), DummyBoundaryStrategy(), DummyContainmentStrategy())
    snapshot = engine.detect("AAPL", "1d", [], base_fingerprint, 1, 1)
    assert len(snapshot.candidates) == 0

def test_engine_detects_consolidation(base_fingerprint):
    engine = ConsolidationDetectionEngine(DummyWindowRequirement(), DummyBoundaryStrategy(), DummyContainmentStrategy())
    base_time = datetime.now(timezone.utc)
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    
    candles = [
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time, open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=1), open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=2), open=1, high=20, low=1, close=15, volume=100), # Breakout
    ]
    
    snapshot = engine.detect("AAPL", "1d", candles, base_fingerprint, 1, 1)
    assert len(snapshot.candidates) == 1
    c = snapshot.candidates[0]
    assert c.candle_count == 2
    assert c.lower_boundary == 1.0
    assert c.upper_boundary == 10.0
    
def test_engine_determinism(base_fingerprint):
    engine = ConsolidationDetectionEngine(DummyWindowRequirement(), DummyBoundaryStrategy(), DummyContainmentStrategy())
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    candles = [
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time, open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=1), open=1, high=10, low=1, close=5, volume=100),
    ]
    
    snap1 = engine.detect("AAPL", "1d", candles, base_fingerprint, 1, 1)
    snap2 = engine.detect("AAPL", "1d", candles, base_fingerprint, 1, 1)
    
    assert snap1.candidates[0].candidate_id == snap2.candidates[0].candidate_id

def test_engine_determinism_stable_ordering(base_fingerprint):
    engine = ConsolidationDetectionEngine(DummyWindowRequirement(), DummyBoundaryStrategy(), DummyContainmentStrategy())
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    
    # Generate two distinct base valid consolidations
    candles1 = [
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time, open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=1), open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=2), open=1, high=20, low=1, close=15, volume=100), # breakout
    ]
    
    # Run the engine
    snap = engine.detect("AAPL", "1d", candles1, base_fingerprint, 1, 1)
    
    # Extract candidate IDs
    candidate_ids = [c.candidate_id for c in snap.candidates]
    
    # Even if internal iteration order changes, or if we sort the output, the generated candidates ID should not depend on iteration order
    # Currently engine detects sequentially, so candidate_ids ordering should just follow timestamp ordering
    
    # As the user recommended, we can verify that snapshot candidate list is stably ordered (e.g., by start_time).
    # Since there's only 1 candidate detected, we can just assert it is present. Let's create another one to test sorting.
    
    candles2 = candles1 + [
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=3), open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=4), open=1, high=10, low=1, close=5, volume=100),
        Candle(symbol=sym, timeframe=Timeframe.D1, timestamp=base_time + timedelta(days=5), open=1, high=20, low=1, close=15, volume=100), # breakout
    ]
    snap2 = engine.detect("AAPL", "1d", candles2, base_fingerprint, 1, 1)
    
    assert len(snap2.candidates) == 2
    # Ensure they are stably sorted by start_timestamp
    assert snap2.candidates[0].start_timestamp < snap2.candidates[1].start_timestamp
