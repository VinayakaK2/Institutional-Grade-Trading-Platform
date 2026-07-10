import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.quality.engine import ConsolidationQualityEngine
from backend.consolidation_engine.quality.models import ConsolidationEvaluationContext, ConsolidationQualityLevel
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
    
    config = ConsolidationQualityConfiguration(
        weight_range_stability=0.2,
        weight_boundary_respect=0.2,
        weight_price_containment=0.2,
        weight_candle_consistency=0.2,
        weight_range_symmetry=0.2
    )
    
    return ConsolidationEvaluationContext(
        candidate=candidate,
        candles=[c1, c2],
        dataset_version=1,
        symbol="AAPL:NASDAQ",
        timeframe="1d",
        configuration=config
    )

def test_quality_engine_evaluation(sample_context):
    engine = ConsolidationQualityEngine(algorithm_version="1.0")
    report = engine.evaluate(sample_context)
    
    assert report.candidate_id == "id1"
    assert report.symbol == "AAPL:NASDAQ"
    # Given all stubs return 1.0, and weights are 0.2 * 5 = 1.0 total score
    # 1.0 > excellent_threshold (0.85) -> EXCELLENT
    assert report.quality_level == ConsolidationQualityLevel.EXCELLENT
    
def test_quality_engine_poor(sample_context):
    config = ConsolidationQualityConfiguration(
        poor_threshold=2.0 # Force a score < poor_threshold to yield REJECTED
    )
    ctx = sample_context.model_copy(update={"configuration": config})
    engine = ConsolidationQualityEngine()
    report = engine.evaluate(ctx)
    assert report.quality_level == ConsolidationQualityLevel.REJECTED
