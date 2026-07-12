import pytest
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LiquidityGrabLifecycleSnapshot,
    LifecycleSummary,
    LiquidityGrabLifecycleState,
    LifecycleEvidence,
    ContinuationEvidence,
    LifecycleEvidenceMetadata
)

def test_lifecycle_snapshot_id_generation():
    snapshot_id = LiquidityGrabLifecycleSnapshot.generate_id(
        candidate_id="c1",
        dataset_version=1,
        config_hash="h1",
        aggregator_version="v1"
    )
    assert snapshot_id is not None
    assert isinstance(snapshot_id, str)
    
def test_models_immutability():
    meta = LifecycleEvidenceMetadata(strategy_version="v", configuration_hash="h", evidence_schema_version="s")
    evidence = ContinuationEvidence(metadata=meta, is_continuing=True, confidence=0.9)
    
    with pytest.raises(Exception):
        evidence.confidence = 0.5
