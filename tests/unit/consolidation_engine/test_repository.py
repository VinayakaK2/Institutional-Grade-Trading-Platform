
import pytest
import asyncio
from datetime import datetime, timezone
from backend.consolidation_engine.repository.memory import InMemoryConsolidationRepository
from backend.consolidation_engine.repository.postgres import PostgreSQLConsolidationRepository
from backend.consolidation_engine.exceptions import ConsolidationRepositoryError
from backend.consolidation_engine.models.models import ConsolidationSnapshot, ConsolidationCandidate

@pytest.fixture
def sample_snapshot():
    c1 = ConsolidationCandidate(
        candidate_id="id1", symbol="AAPL:NASDAQ", timeframe="1d",
        start_timestamp=datetime.now(timezone.utc), end_timestamp=datetime.now(timezone.utc),
        upper_boundary=10, lower_boundary=1, midpoint=5.5, duration=86400, candle_count=2
    )
    
    return ConsolidationSnapshot(
        snapshot_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=10,
        pipeline_version="1.0",
        config_version=1,
        config_hash="abc",
        business_fingerprint="fp1",
        fingerprint_algorithm_version=1,
        candidates=[c1]
    )

@pytest.mark.asyncio
async def test_memory_repo(sample_snapshot):
    repo = InMemoryConsolidationRepository()
    await repo.save_snapshot(sample_snapshot)
    
    loaded = await repo.load_snapshot_by_version(1)
    assert loaded == sample_snapshot
    
    latest = await repo.load_latest_snapshot()
    assert latest == sample_snapshot
    
    assert await repo.exists(1) is True
    assert await repo.exists(2) is False
    
    with pytest.raises(ConsolidationRepositoryError):
        await repo.save_snapshot(sample_snapshot)

@pytest.mark.asyncio
async def test_memory_repo_historical(sample_snapshot):
    repo = InMemoryConsolidationRepository()
    await repo.save_snapshot(sample_snapshot)
    
    s2 = sample_snapshot.model_copy(update={"snapshot_version": 2, "parent_trend_snapshot_version": 20})
    await repo.save_snapshot(s2)
    
    hist = await repo.load_historical_snapshots(limit=10)
    assert len(hist) == 2
    assert hist[0].snapshot_version == 2
    assert hist[1].snapshot_version == 1

@pytest.mark.asyncio
async def test_memory_repo_queries(sample_snapshot):
    repo = InMemoryConsolidationRepository()
    await repo.save_snapshot(sample_snapshot)
    
    assert len(await repo.query_by_parent_trend_snapshot(10)) == 1
    assert len(await repo.query_by_parent_trend_snapshot(20)) == 0
    
    assert len(await repo.query_by_symbol("AAPL:NASDAQ")) == 1
    assert len(await repo.query_by_symbol("MSFT:NASDAQ")) == 0
    
    assert len(await repo.query_by_timeframe("1d")) == 1
    assert len(await repo.query_by_timeframe("1h")) == 0

@pytest.mark.asyncio
async def test_postgres_repo(sample_snapshot):
    repo = PostgreSQLConsolidationRepository(None)
    await repo.save_snapshot(sample_snapshot)
    
    assert await repo.load_latest_snapshot() is None
    assert await repo.load_snapshot_by_version(1) is None
    assert await repo.load_historical_snapshots() == []
    assert await repo.exists(1) is False
    assert await repo.query_by_parent_trend_snapshot(10) == []
    assert await repo.query_by_symbol("AAPL:NASDAQ") == []
    assert await repo.query_by_timeframe("1d") == []
