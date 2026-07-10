import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.lifecycle.models import (
    ConsolidationLifecycleContext,
    ContinuationEvidence,
    WeakeningEvidence,
    BreakEvidence,
    EndEvidence
)
from backend.consolidation_engine.lifecycle.evidence import (
    ContinuationEvidenceEvaluator,
    WeakeningEvidenceEvaluator,
    BreakEvidenceEvaluator,
    EndEvidenceEvaluator
)
from backend.consolidation_engine.quality.models import ConsolidationQualityReport, ConsolidationQualityMetrics, ConsolidationQualityLevel
from backend.consolidation_engine.models.models import ConsolidationCandidate
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.consolidation_engine.lifecycle.config import ConsolidationLifecycleConfiguration

@pytest.fixture
def sample_context():
    candidate = ConsolidationCandidate(
        candidate_id="id1", symbol="AAPL:NASDAQ", timeframe="1d",
        start_timestamp=datetime.now(timezone.utc), end_timestamp=datetime.now(timezone.utc),
        upper_boundary=110, lower_boundary=100, midpoint=105, duration=86400, candle_count=2
    )
    metrics = ConsolidationQualityMetrics(
        range_stability=1.0, boundary_respect=1.0, price_containment=1.0,
        candle_consistency=1.0, consolidation_duration=2, range_symmetry=1.0
    )
    report = ConsolidationQualityReport(
        report_id="r1", candidate_id="id1", symbol="AAPL:NASDAQ", timeframe="1d",
        metrics=metrics, quality_level=ConsolidationQualityLevel.EXCELLENT,
        config_version=1, algorithm_version="1.0"
    )
    return ConsolidationLifecycleContext(
        candidate=candidate,
        quality_report=report,
        evaluation_candles=[],
        configuration=ConsolidationLifecycleConfiguration()
    )

def test_continuation_evidence(sample_context):
    evaluator = ContinuationEvidenceEvaluator()
    evidence = evaluator.evaluate(sample_context)
    assert isinstance(evidence, ContinuationEvidence)

def test_weakening_evidence(sample_context):
    evaluator = WeakeningEvidenceEvaluator()
    evidence = evaluator.evaluate(sample_context)
    assert isinstance(evidence, WeakeningEvidence)

def test_break_evidence(sample_context):
    evaluator = BreakEvidenceEvaluator()
    evidence = evaluator.evaluate(sample_context)
    assert isinstance(evidence, BreakEvidence)

def test_end_evidence(sample_context):
    evaluator = EndEvidenceEvaluator()
    evidence = evaluator.evaluate(sample_context)
    assert isinstance(evidence, EndEvidence)
