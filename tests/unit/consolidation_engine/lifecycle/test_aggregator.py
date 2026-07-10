import pytest
from backend.consolidation_engine.lifecycle.models import (
    ConsolidationLifecycleState,
    ContinuationEvidence,
    WeakeningEvidence,
    BreakEvidence,
    EndEvidence
)
from backend.consolidation_engine.lifecycle.config import ConsolidationLifecycleConfiguration
from backend.consolidation_engine.lifecycle.aggregator import LifecycleAggregator

@pytest.fixture
def config():
    return ConsolidationLifecycleConfiguration()

def test_aggregator_precedence_all_triggered(config):
    evidence_list = [
        ContinuationEvidence(triggered=True, confidence=1.0, reason="test"),
        WeakeningEvidence(triggered=True, confidence=1.0, reason="test"),
        BreakEvidence(triggered=True, confidence=1.0, reason="test"),
        EndEvidence(triggered=True, confidence=1.0, reason="test")
    ]
    state = LifecycleAggregator.resolve_state(evidence_list, config)
    assert state == ConsolidationLifecycleState.ENDED

def test_aggregator_precedence_break_wins(config):
    evidence_list = [
        ContinuationEvidence(triggered=True, confidence=1.0, reason="test"),
        WeakeningEvidence(triggered=True, confidence=1.0, reason="test"),
        BreakEvidence(triggered=True, confidence=1.0, reason="test"),
        EndEvidence(triggered=False, confidence=1.0, reason="test")
    ]
    state = LifecycleAggregator.resolve_state(evidence_list, config)
    assert state == ConsolidationLifecycleState.BROKEN

def test_aggregator_precedence_active(config):
    evidence_list = [
        ContinuationEvidence(triggered=False, confidence=1.0, reason="test"),
        WeakeningEvidence(triggered=False, confidence=1.0, reason="test"),
        BreakEvidence(triggered=False, confidence=1.0, reason="test"),
        EndEvidence(triggered=False, confidence=1.0, reason="test")
    ]
    state = LifecycleAggregator.resolve_state(evidence_list, config)
    assert state == ConsolidationLifecycleState.ACTIVE
    
def test_deterministic_conflict_resolution():
    """
    Mandatory regression test: Continuation=True, Weakening=True, Break=True -> Expected: BROKEN
    """
    config = ConsolidationLifecycleConfiguration(
        # We ensure ENDED is not in the list for this specific scenario
        state_precedence=["BROKEN", "WEAKENING", "CONTINUING", "ACTIVE"]
    )
    evidence_list = [
        ContinuationEvidence(triggered=True, confidence=0.99, reason="test"),
        WeakeningEvidence(triggered=True, confidence=0.99, reason="test"),
        BreakEvidence(triggered=True, confidence=0.01, reason="test"), # Low confidence shouldn't matter
    ]
    state = LifecycleAggregator.resolve_state(evidence_list, config)
    assert state == ConsolidationLifecycleState.BROKEN
