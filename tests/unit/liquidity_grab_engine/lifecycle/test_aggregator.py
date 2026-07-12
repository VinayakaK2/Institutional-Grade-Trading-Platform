from backend.liquidity_grab_engine.lifecycle.aggregator.default import DefaultLifecycleAggregator
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LifecycleEvidence,
    LiquidityGrabLifecycleState,
    FailureEvidence,
    ExpirationEvidence,
    WeakeningEvidence,
    ContinuationEvidence,
    LifecycleEvidenceMetadata
)

def test_default_lifecycle_aggregator():
    aggregator = DefaultLifecycleAggregator()
    meta = LifecycleEvidenceMetadata(strategy_version="v", configuration_hash="h", evidence_schema_version="s")
    
    # Active State
    evidence_active = LifecycleEvidence()
    summary = aggregator.aggregate(evidence_active)
    assert summary.state == LiquidityGrabLifecycleState.ACTIVE
    assert summary.decision_reason == "Default active state"
    
    # Continuing State
    cont_ev = ContinuationEvidence(metadata=meta, is_continuing=True, confidence=0.8, reason="Strong continuation")
    evidence_cont = LifecycleEvidence(continuation_evidence=cont_ev)
    summary = aggregator.aggregate(evidence_cont)
    assert summary.state == LiquidityGrabLifecycleState.CONTINUING
    assert summary.decision_reason == "Strong continuation"
    
    # Weakening overrides Continuing
    weak_ev = WeakeningEvidence(metadata=meta, is_weakening=True, confidence=0.9, reason="Momentum loss")
    evidence_weak = LifecycleEvidence(continuation_evidence=cont_ev, weakening_evidence=weak_ev)
    summary = aggregator.aggregate(evidence_weak)
    assert summary.state == LiquidityGrabLifecycleState.WEAKENING
    assert summary.decision_reason == "Momentum loss"
    
    # Expired overrides Weakening
    exp_ev = ExpirationEvidence(metadata=meta, is_expired=True, confidence=1.0, reason="Time bound hit")
    evidence_exp = LifecycleEvidence(continuation_evidence=cont_ev, weakening_evidence=weak_ev, expiration_evidence=exp_ev)
    summary = aggregator.aggregate(evidence_exp)
    assert summary.state == LiquidityGrabLifecycleState.EXPIRED
    assert summary.decision_reason == "Time bound hit"
    
    # Failed overrides Expired
    fail_ev = FailureEvidence(metadata=meta, is_failed=True, confidence=1.0, reason="Support broken")
    evidence_fail = LifecycleEvidence(continuation_evidence=cont_ev, weakening_evidence=weak_ev, expiration_evidence=exp_ev, failure_evidence=fail_ev)
    summary = aggregator.aggregate(evidence_fail)
    assert summary.state == LiquidityGrabLifecycleState.FAILED
    assert summary.decision_reason == "Support broken"
