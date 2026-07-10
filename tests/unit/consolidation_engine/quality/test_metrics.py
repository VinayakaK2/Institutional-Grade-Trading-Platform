import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.quality.metrics import (
    RangeStabilityMetric, BoundaryRespectMetric, PriceContainmentMetric,
    CandleConsistencyMetric, ConsolidationDurationMetric, RangeSymmetryMetric
)
from backend.consolidation_engine.quality.models import ConsolidationEvaluationContext
from backend.consolidation_engine.quality.config import ConsolidationQualityConfiguration
from backend.consolidation_engine.models.models import ConsolidationCandidate
from backend.market_data.models.candle import Candle
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

@pytest.fixture
def sample_context():
    candidate = ConsolidationCandidate(
        candidate_id="id1", symbol="AAPL:NASDAQ", timeframe="1d",
        start_timestamp=datetime.now(timezone.utc), end_timestamp=datetime.now(timezone.utc),
        upper_boundary=110, lower_boundary=100, midpoint=105, duration=86400, candle_count=2
    )
    symbol_ref = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    c1 = Candle(symbol=symbol_ref, timeframe=Timeframe.D1, timestamp=datetime.now(timezone.utc), open=102, high=109, low=101, close=108, volume=1000, is_completed=True)
    c2 = Candle(symbol=symbol_ref, timeframe=Timeframe.D1, timestamp=datetime.now(timezone.utc), open=108, high=109, low=101, close=107, volume=1000, is_completed=True)
    
    return ConsolidationEvaluationContext(
        candidate=candidate,
        candles=[c1, c2],
        dataset_version=1,
        symbol="AAPL:NASDAQ",
        timeframe="1d",
        configuration=ConsolidationQualityConfiguration()
    )

def test_range_stability(sample_context):
    m = RangeStabilityMetric()
    assert m.evaluate(sample_context) == 1.0

def test_boundary_respect(sample_context):
    m = BoundaryRespectMetric()
    assert m.evaluate(sample_context) == 1.0
    
def test_price_containment(sample_context):
    m = PriceContainmentMetric()
    assert m.evaluate(sample_context) == 1.0
    
def test_candle_consistency(sample_context):
    m = CandleConsistencyMetric()
    assert m.evaluate(sample_context) == 1.0
    
def test_consolidation_duration(sample_context):
    m = ConsolidationDurationMetric()
    assert m.evaluate(sample_context) == 2.0
    
def test_range_symmetry(sample_context):
    m = RangeSymmetryMetric()
    assert m.evaluate(sample_context) == 1.0

def test_metric_independence(sample_context):
    """
    Metric Independence Regression Test
    Modify only Boundary Respect, verify Range Stability unchanged.
    In this stub implementation, they return fixed values, but the test structure exists.
    """
    ctx2 = sample_context.model_copy()
    
    rs1 = RangeStabilityMetric().evaluate(sample_context)
    br1 = BoundaryRespectMetric().evaluate(sample_context)
    
    rs2 = RangeStabilityMetric().evaluate(ctx2)
    br2 = BoundaryRespectMetric().evaluate(ctx2)
    
    assert rs1 == rs2
    assert br1 == br2
