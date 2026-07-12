import pytest
import unittest.mock as mock
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate, DetectionEvidence, CandidateMetadata, CandidateVersion
from backend.liquidity_grab_engine.detection.repository.memory import InMemoryDetectionRepository
from backend.liquidity_grab_engine.detection.repository.postgres import PostgreSQLDetectionRepository

def create_candidate(cid: str, dataset: int, trend: int, cons: int) -> LiquidityGrabCandidate:
    return LiquidityGrabCandidate(
        candidate_id=cid,
        symbol_id="AAPL",
        timeframe="1h",
        dataset_version=dataset,
        parent_trend_snapshot_version=trend,
        parent_consolidation_snapshot_version=cons,
        configuration_hash="abc",
        evidence=DetectionEvidence(),
        metadata=CandidateMetadata(pipeline_version="1.0"),
        version=CandidateVersion()
    )

@pytest.mark.asyncio
async def test_memory_repo():
    repo = InMemoryDetectionRepository()
    c1 = create_candidate("1", 1, 10, 20)
    c2 = create_candidate("2", 1, 10, 20)
    c3 = create_candidate("3", 2, 11, 21)
    
    await repo.save(c1)
    await repo.save(c2)
    await repo.save(c3)
    
    assert await repo.exists("1") is True
    assert await repo.exists("999") is False
    
    loaded = await repo.load("1")
    assert loaded is not None
    assert loaded.candidate_id == "1"
    
    by_sym = await repo.query_by_symbol("AAPL")
    assert len(by_sym) == 3
    
    by_tf = await repo.query_by_timeframe("1h")
    assert len(by_tf) == 3
    
    by_dataset = await repo.query_by_dataset_version(1)
    assert len(by_dataset) == 2
    
    by_trend = await repo.query_by_parent_trend_snapshot(11)
    assert len(by_trend) == 1
    assert by_trend[0].candidate_id == "3"
    
    by_cons = await repo.query_by_parent_consolidation_snapshot(20)
    assert len(by_cons) == 2
    
    latest = await repo.load_latest()
    assert latest is not None

@pytest.mark.asyncio
async def test_memory_repo_empty():
    repo = InMemoryDetectionRepository()
    assert await repo.load_latest() is None

@pytest.mark.asyncio
async def test_postgres_unimplemented():
    repo = PostgreSQLDetectionRepository(None)
    with pytest.raises(NotImplementedError):
        await repo.save(create_candidate("1",1,1,1))
    with pytest.raises(NotImplementedError):
        await repo.load("1")
    with pytest.raises(NotImplementedError):
        await repo.exists("1")
    with pytest.raises(NotImplementedError):
        await repo.query_by_symbol("AAPL")
    with pytest.raises(NotImplementedError):
        await repo.query_by_timeframe("1h")
    with pytest.raises(NotImplementedError):
        await repo.query_by_parent_trend_snapshot(1)
    with pytest.raises(NotImplementedError):
        await repo.query_by_parent_consolidation_snapshot(1)
    with pytest.raises(NotImplementedError):
        await repo.query_by_dataset_version(1)
    with pytest.raises(NotImplementedError):
        await repo.load_latest()
