import pytest
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate, DetectionEvidence

def test_deterministic_id_generation():
    id1 = LiquidityGrabCandidate.generate_id(
        symbol_id="AAPL",
        dataset_version=1,
        trend_version=2,
        consolidation_version=3,
        config_hash="abc"
    )
    
    id2 = LiquidityGrabCandidate.generate_id(
        symbol_id="AAPL",
        dataset_version=1,
        trend_version=2,
        consolidation_version=3,
        config_hash="abc"
    )
    
    id3 = LiquidityGrabCandidate.generate_id(
        symbol_id="MSFT",
        dataset_version=1,
        trend_version=2,
        consolidation_version=3,
        config_hash="abc"
    )
    
    assert id1 == id2
    assert id1 != id3

def test_evidence_immutability():
    ev = DetectionEvidence(support_break_detected=True)
    with pytest.raises(Exception): # Pydantic v2 raises ValidationError on frozen models
        ev.support_break_detected = False
