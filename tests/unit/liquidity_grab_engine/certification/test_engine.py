import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.certification.engine.engine import LiquidityGrabCertificationEngine
from backend.liquidity_grab_engine.certification.models.models import CertificationContext
from backend.liquidity_grab_engine.certification.repository.memory import InMemoryCertificationRepository
from backend.liquidity_grab_engine.optimization.models.models import OptimizationSnapshot, BusinessFingerprint, OptimizationMetadata, OptimizationRuntimeStatistics
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot, LifecycleSummary, LiquidityGrabLifecycleState, LifecycleEvidence

def create_mock_snapshot(cand_id: str = "c1") -> OptimizationSnapshot:
    bf = BusinessFingerprint(
        candidate_id=cand_id,
        dataset_version=1,
        config_hash="h",
        detection_algorithm_version="v1",
        quality_algorithm_version="v2",
        lifecycle_algorithm_version="v3"
    )
    ls = LiquidityGrabLifecycleSnapshot(
        snapshot_id=f"ls_{cand_id}",
        candidate_id=cand_id,
        symbol_id="sym1",
        timeframe="H1",
        evidence=LifecycleEvidence(),
        metadata={},
        summary=LifecycleSummary(state=LiquidityGrabLifecycleState.ACTIVE, aggregator_version="1.0.0")
    )
    meta = OptimizationMetadata(optimization_engine_version="1.0", optimization_timestamp=0.0)
    stats = OptimizationRuntimeStatistics(
        candidates_processed=1,
        candidates_reused=0,
        cache_hits=0,
        cache_misses=1,
        batch_count=1,
        execution_duration_ms=10.0
    )
    
    return OptimizationSnapshot(
        snapshot_id=f"os_{cand_id}",
        business_fingerprint=bf,
        lifecycle_snapshot=ls,
        metadata=meta,
        runtime_statistics=stats
    )

@pytest.fixture
def mock_optimization_engine():
    engine = MagicMock()
    # Mocking the execute_batch method to just return generic snapshots based on the input lengths
    async def mock_execute_batch(contexts, opt_context):
        return [create_mock_snapshot(cand_id=c.candidate.candidate_id if hasattr(c, 'candidate') else f"c_{i}") for i, c in enumerate(contexts)]
    engine.execute_batch = mock_execute_batch
    return engine

@pytest.mark.asyncio
async def test_certification_engine(mock_optimization_engine):
    repo = InMemoryCertificationRepository()
    engine = LiquidityGrabCertificationEngine(
        optimization_engine=mock_optimization_engine,
        repository=repo
    )
    
    # We will use small stress_test_sizes to keep test fast
    ctx = CertificationContext(stress_test_sizes=[1, 2], run_performance_benchmarks=True)
    report = await engine.execute(ctx)
    
    assert report is not None
    assert report.summary.is_certified is True
    
    # Check that phases exist
    assert len(report.summary.phase_results) == 5
    
    for r in report.summary.phase_results:
        assert r.success is True
        
    assert await repo.exists(report.report_id) is True

@pytest.mark.asyncio
async def test_certification_engine_failure_fast(mock_optimization_engine):
    # Make the optimization engine return incorrect number of results to force a functional failure
    async def mock_execute_batch_bad(contexts, opt_context):
        return []
    
    mock_optimization_engine.execute_batch = mock_execute_batch_bad
    
    repo = InMemoryCertificationRepository()
    engine = LiquidityGrabCertificationEngine(
        optimization_engine=mock_optimization_engine,
        repository=repo
    )
    
    ctx = CertificationContext(fail_fast=True)
    report = await engine.execute(ctx)
    
    assert report.summary.is_certified is False
    # Since fail_fast is true, it should abort after the first failure (Functional)
    assert len(report.summary.phase_results) == 1
    assert report.summary.phase_results[0].success is False
