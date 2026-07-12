import pytest
from backend.liquidity_grab_engine.optimization.models.models import (
    BusinessFingerprint,
    OptimizationContext,
    OptimizationRuntimeStatistics,
    OptimizationMetadata,
)

def test_business_fingerprint_determinism():
    bf1 = BusinessFingerprint(
        candidate_id="cand_1",
        dataset_version=1,
        config_hash="abc",
        detection_algorithm_version="v1",
        quality_algorithm_version="v2",
        lifecycle_algorithm_version="v3"
    )
    
    bf2 = BusinessFingerprint(
        candidate_id="cand_1",
        dataset_version=1,
        config_hash="abc",
        detection_algorithm_version="v1",
        quality_algorithm_version="v2",
        lifecycle_algorithm_version="v3"
    )
    
    # Must be identical hashes
    assert bf1.fingerprint_hash == bf2.fingerprint_hash
    
def test_business_fingerprint_differences():
    bf1 = BusinessFingerprint(
        candidate_id="cand_1",
        dataset_version=1,
        config_hash="abc",
        detection_algorithm_version="v1",
        quality_algorithm_version="v2",
        lifecycle_algorithm_version="v3"
    )
    
    bf2 = BusinessFingerprint(
        candidate_id="cand_1",
        dataset_version=2,  # Diff
        config_hash="abc",
        detection_algorithm_version="v1",
        quality_algorithm_version="v2",
        lifecycle_algorithm_version="v3"
    )
    
    assert bf1.fingerprint_hash != bf2.fingerprint_hash

def test_optimization_context_defaults():
    ctx = OptimizationContext()
    assert ctx.cache_enabled is True
    assert ctx.reuse_enabled is True
    assert ctx.batch_size == 50
    assert ctx.max_parallelism == 4
