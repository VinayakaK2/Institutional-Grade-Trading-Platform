from backend.trend_engine.lifecycle.models.models import (
    TrendLifecycleState,
    ContinuationEvidence,
    WeakeningEvidence,
    BreakEvidence,
    EndEvidence,
    TrendLifecycleSymbolResult,
    TrendLifecycleSnapshot
)

def test_evidence_models():
    ce = ContinuationEvidence(is_continuing=True, reason="ok")
    we = WeakeningEvidence(is_weakening=False, reason="ok")
    be = BreakEvidence(is_broken=False, reason="ok")
    ee = EndEvidence(is_ended=False, reason="ok")
    
    assert ce.is_continuing is True
    assert we.is_weakening is False
    assert be.is_broken is False
    assert ee.is_ended is False

def test_symbol_result():
    res = TrendLifecycleSymbolResult(
        symbol_key="AAPL:NASDAQ",
        final_state=TrendLifecycleState.CONTINUING
    )
    assert res.symbol_key == "AAPL:NASDAQ"
    assert res.final_state == TrendLifecycleState.CONTINUING
    assert res.continuation_evidence is None

def test_snapshot_model():
    snapshot = TrendLifecycleSnapshot(
        snapshot_id="l_1",
        parent_trend_snapshot_id="t_1",
        parent_trend_quality_snapshot_id="q_1",
        symbols={},
        pipeline_version="1.0.0",
        configuration_hash="hash",
        lifecycle_algorithm_version="1.0.0",
        lifecycle_rule_version=1
    )
    assert snapshot.snapshot_id == "l_1"
    assert snapshot.parent_trend_snapshot_id == "t_1"
    assert snapshot.metadata is not None
