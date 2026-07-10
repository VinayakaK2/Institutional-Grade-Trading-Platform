import pytest
import asyncio
from datetime import datetime, timezone
from backend.consolidation_engine.lifecycle.repository.memory import InMemoryConsolidationLifecycleRepository
from backend.consolidation_engine.lifecycle.repository.postgres import PostgreSQLConsolidationLifecycleRepository
from backend.consolidation_engine.lifecycle.models import ConsolidationLifecycleSnapshot, ConsolidationLifecycleState
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError

@pytest.fixture
def memory_repo():
    return InMemoryConsolidationLifecycleRepository()
    
@pytest.fixture
def sample_snapshot():
    return ConsolidationLifecycleSnapshot(
        snapshot_id="snap1",
        candidate_id="cand1",
        quality_report_id="qual1",
        parent_candidate_snapshot_version=1,
        quality_report_version=1,
        configuration_version=1,
        lifecycle_rule_version="1.0",
        lifecycle_algorithm_version="1.0",
        symbol="AAPL",
        timeframe="1d",
        lifecycle_state=ConsolidationLifecycleState.ACTIVE,
        supporting_evidence=[],
        generated_timestamp=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_memory_repo_save_and_load(memory_repo, sample_snapshot):
    await memory_repo.save(sample_snapshot)
    
    exists = await memory_repo.exists("snap1")
    assert exists is True
    
    loaded = await memory_repo.load_by_snapshot_id("snap1")
    assert loaded == sample_snapshot
    
    latest = await memory_repo.load_latest("cand1")
    assert latest == sample_snapshot
    
@pytest.mark.asyncio
async def test_memory_repo_duplicate_save(memory_repo, sample_snapshot):
    await memory_repo.save(sample_snapshot)
    with pytest.raises(ConsolidationRepositoryError):
        await memory_repo.save(sample_snapshot)

@pytest.mark.asyncio
async def test_memory_repo_queries(memory_repo, sample_snapshot):
    await memory_repo.save(sample_snapshot)
    
    by_symbol = await memory_repo.query_by_symbol("AAPL")
    assert len(by_symbol) == 1
    
    by_timeframe = await memory_repo.query_by_timeframe("1d")
    assert len(by_timeframe) == 1
    
    by_state = await memory_repo.query_by_state(ConsolidationLifecycleState.ACTIVE)
    assert len(by_state) == 1

@pytest.mark.asyncio
async def test_postgres_repo_stubs(sample_snapshot):
    repo = PostgreSQLConsolidationLifecycleRepository(session_factory=None)
    # Just to ensure it implements the contract without errors
    await repo.save(sample_snapshot)
    assert await repo.exists("snap1") is False
    assert await repo.load_by_snapshot_id("snap1") is None
    assert await repo.load_latest("cand1") is None
    assert len(await repo.query_by_symbol("AAPL")) == 0
    assert len(await repo.query_by_timeframe("1d")) == 0
    assert len(await repo.query_by_state(ConsolidationLifecycleState.ACTIVE)) == 0
