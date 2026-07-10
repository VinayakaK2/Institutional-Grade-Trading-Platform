import pytest
from datetime import datetime, timezone
from backend.consolidation_engine.optimization.models import (
    BusinessFingerprint,
    ConsolidationOptimizationSnapshot,
    OptimizationBusinessStatistics,
    OptimizationRuntimeStatistics
)

def test_business_fingerprint_determinism():
    """Verify that identical inputs produce the same fingerprint (SHA-256)."""
    fp1 = BusinessFingerprint(
        fingerprint_version="1.0",
        candidate_id="cand_123",
        candidate_version=1,
        quality_report_version=2,
        lifecycle_snapshot_version=3,
        configuration_hash="hashXYZ",
        algorithm_versions="alg_1.0"
    )
    
    fp2 = BusinessFingerprint(
        fingerprint_version="1.0",
        candidate_id="cand_123",
        candidate_version=1,
        quality_report_version=2,
        lifecycle_snapshot_version=3,
        configuration_hash="hashXYZ",
        algorithm_versions="alg_1.0"
    )
    
    assert fp1.digest == fp2.digest
    
    fp3 = BusinessFingerprint(
        fingerprint_version="1.0",
        candidate_id="cand_123",
        candidate_version=2, # Changed version
        quality_report_version=2,
        lifecycle_snapshot_version=3,
        configuration_hash="hashXYZ",
        algorithm_versions="alg_1.0"
    )
    
    assert fp1.digest != fp3.digest


def test_snapshot_generation():
    """Verify snapshot IDs are generated correctly."""
    biz = OptimizationBusinessStatistics(total_candidates=10)
    run = OptimizationRuntimeStatistics(execution_time_ms=100.0)
    
    ts = datetime.now(timezone.utc)
    fingerprint = "dummy_fingerprint"
    
    snapshot_id = ConsolidationOptimizationSnapshot.generate_id(fingerprint, ts)
    
    snap = ConsolidationOptimizationSnapshot(
        snapshot_id=snapshot_id,
        business_fingerprint=fingerprint,
        fingerprint_version="1.0",
        optimization_algorithm_version="1.0",
        business_statistics=biz,
        runtime_statistics=run,
        configuration_version=1,
        generated_timestamp=ts
    )
    
    assert snap.snapshot_id == snapshot_id
    assert snap.business_statistics.total_candidates == 10
