import pytest
from backend.liquidity_grab_engine.optimization.repository.memory import InMemoryOptimizationRepository
from backend.liquidity_grab_engine.optimization.repository.postgres import PostgreSQLOptimizationRepository
from backend.liquidity_grab_engine.optimization.models.models import (
    OptimizationSnapshot, 
    BusinessFingerprint,
    OptimizationMetadata,
    OptimizationRuntimeStatistics
)
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LiquidityGrabLifecycleSnapshot,
    LifecycleSummary,
    LiquidityGrabLifecycleState,
    LifecycleEvidence
)

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
        snapshot_id="ls_1",
        candidate_id=cand_id,
        symbol_id="sym1",
        timeframe="H1",
        evidence=LifecycleEvidence(),
        metadata={},
        summary=LifecycleSummary(state=LiquidityGrabLifecycleState.ACTIVE, aggregator_version="1.0.0")
    )
    meta = OptimizationMetadata(optimization_engine_version="1.0", optimization_timestamp=0.0)
    stats = OptimizationRuntimeStatistics()
    
    return OptimizationSnapshot(
        snapshot_id="os_1",
        business_fingerprint=bf,
        lifecycle_snapshot=ls,
        metadata=meta,
        runtime_statistics=stats
    )

@pytest.mark.asyncio
async def test_memory_repository():
    repo = InMemoryOptimizationRepository()
    
    snap1 = create_mock_snapshot("c1")
    snap2 = create_mock_snapshot("c2")
    
    assert await repo.exists(snap1.business_fingerprint.fingerprint_hash) is False
    assert await repo.load_latest() is None
    
    await repo.save(snap1)
    await repo.save(snap2)
    
    assert await repo.exists(snap1.business_fingerprint.fingerprint_hash) is True
    
    loaded = await repo.load(snap1.business_fingerprint.fingerprint_hash)
    assert loaded is not None
    assert loaded.snapshot_id == snap1.snapshot_id
    
    latest = await repo.load_latest()
    assert latest is not None
    assert latest.snapshot_id == snap2.snapshot_id
    
    by_cand = await repo.query_by_candidate("c1")
    assert len(by_cand) == 1
    assert by_cand[0].snapshot_id == snap1.snapshot_id

@pytest.mark.asyncio
async def test_postgres_repository_stub():
    repo = PostgreSQLOptimizationRepository()
    snap = create_mock_snapshot("c1")
    
    with pytest.raises(NotImplementedError):
        await repo.save(snap)
        
    with pytest.raises(NotImplementedError):
        await repo.exists("abc")
        
    with pytest.raises(NotImplementedError):
        await repo.load("abc")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_candidate("c1")
        
    with pytest.raises(NotImplementedError):
        await repo.load_latest()
