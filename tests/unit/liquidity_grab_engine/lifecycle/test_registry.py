from unittest.mock import MagicMock
from backend.liquidity_grab_engine.lifecycle.registry.registry import EvidenceRegistry
from backend.liquidity_grab_engine.lifecycle.contracts.evidence import IContinuationStrategy, IWeakeningStrategy, IFailureStrategy, IExpirationStrategy
from backend.liquidity_grab_engine.lifecycle.models.models import ContinuationEvidence, WeakeningEvidence, FailureEvidence, ExpirationEvidence, LifecycleEvidenceMetadata

def test_registry_execution():
    registry = EvidenceRegistry()
    meta = LifecycleEvidenceMetadata(strategy_version="v1", configuration_hash="h1", evidence_schema_version="e1")
    
    mock_strat = MagicMock(spec=IContinuationStrategy)
    mock_strat.priority = 1
    mock_strat.strategy_id = "s1"
    mock_ev = ContinuationEvidence(metadata=meta, is_continuing=True, confidence=0.8)
    mock_strat.evaluate.return_value = mock_ev
    registry.register_continuation(mock_strat)
    
    mock_weak = MagicMock(spec=IWeakeningStrategy)
    mock_weak.priority = 1
    mock_weak.strategy_id = "w1"
    mock_ev_w = WeakeningEvidence(metadata=meta, is_weakening=True, confidence=0.9)
    mock_weak.evaluate.return_value = mock_ev_w
    registry.register_weakening(mock_weak)
    
    mock_fail = MagicMock(spec=IFailureStrategy)
    mock_fail.priority = 1
    mock_fail.strategy_id = "f1"
    mock_ev_f = FailureEvidence(metadata=meta, is_failed=True, confidence=0.5)
    mock_fail.evaluate.return_value = mock_ev_f
    registry.register_failure(mock_fail)
    
    mock_exp = MagicMock(spec=IExpirationStrategy)
    mock_exp.priority = 1
    mock_exp.strategy_id = "e1"
    mock_ev_e = ExpirationEvidence(metadata=meta, is_expired=True, confidence=0.1)
    mock_exp.evaluate.return_value = mock_ev_e
    registry.register_expiration(mock_exp)
    
    mock_context = MagicMock()
    evidence = registry.execute(mock_context)
    
    assert evidence.continuation_evidence == mock_ev
    assert evidence.weakening_evidence == mock_ev_w
    assert evidence.failure_evidence == mock_ev_f
    assert evidence.expiration_evidence == mock_ev_e
