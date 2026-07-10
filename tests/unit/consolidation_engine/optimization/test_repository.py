import pytest
import asyncio
from datetime import datetime, timezone
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.optimization.repository.memory import InMemoryConsolidationOptimizationRepository
from backend.consolidation_engine.optimization.models import (
    ConsolidationOptimizationSnapshot,
    OptimizationBusinessStatistics,
    OptimizationRuntimeStatistics
)

@pytest.fixture
def repo():
    return InMemoryConsolidationOptimizationRepository()
    
def create_snapshot(snapshot_id: str, fingerprint: str, parent: str = None) -> ConsolidationOptimizationSnapshot:
    biz = OptimizationBusinessStatistics(total_candidates=1)
    run = OptimizationRuntimeStatistics(execution_time_ms=10.0)
    ts = datetime.now(timezone.utc)
    return ConsolidationOptimizationSnapshot(
        snapshot_id=snapshot_id,
        parent_snapshot_id=parent,
        business_fingerprint=fingerprint,
        fingerprint_version="1.0",
        optimization_algorithm_version="1.0",
        business_statistics=biz,
        runtime_statistics=run,
        configuration_version=1,
        generated_timestamp=ts
    )

@pytest.mark.asyncio
async def test_repository_save_and_load(repo):
    snap1 = create_snapshot("snap1", "finger1")
    await repo.save(snap1)
    
    assert await repo.exists("finger1") is True
    assert await repo.exists("finger2") is False
    
    loaded = await repo.load_by_fingerprint("finger1")
    assert loaded is not None
    assert loaded.snapshot_id == "snap1"
    
@pytest.mark.asyncio
async def test_repository_idempotent_insert_failure(repo):
    snap1 = create_snapshot("snap1", "finger1")
    await repo.save(snap1)
    
    with pytest.raises(ConsolidationRepositoryError):
        await repo.save(snap1)
        
@pytest.mark.asyncio
async def test_repository_load_latest(repo):
    snap1 = create_snapshot("snap1", "finger1")
    await asyncio.sleep(0.01)
    snap2 = create_snapshot("snap2", "finger2")
    
    await repo.save(snap1)
    await repo.save(snap2)
    
    latest = await repo.load_latest()
    assert latest is not None
    assert latest.snapshot_id == "snap2"
    
@pytest.mark.asyncio
async def test_repository_query_by_parent(repo):
    snap1 = create_snapshot("snap1", "finger1", parent="parent1")
    snap2 = create_snapshot("snap2", "finger2", parent="parent1")
    snap3 = create_snapshot("snap3", "finger3", parent="parent2")
    
    await repo.save(snap1)
    await repo.save(snap2)
    await repo.save(snap3)
    
    children = await repo.query_by_parent("parent1")
    assert len(children) == 2
    assert any(c.snapshot_id == "snap1" for c in children)
