import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.lifecycle.repository.memory import InMemoryLifecycleRepository
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot, LiquidityGrabLifecycleState

@pytest.mark.asyncio
async def test_in_memory_repository():
    repo = InMemoryLifecycleRepository()
    
    mock_snapshot_1 = MagicMock(spec=LiquidityGrabLifecycleSnapshot)
    mock_snapshot_1.snapshot_id = "s1"
    mock_snapshot_1.candidate_id = "c1"
    mock_snapshot_1.symbol_id = "BTC"
    mock_snapshot_1.summary = MagicMock()
    mock_snapshot_1.summary.state = LiquidityGrabLifecycleState.ACTIVE
    mock_snapshot_1.metadata = {"generated_at": "2023-01-01T00:00:00Z", "quality_report_id": "q1"}
    
    mock_snapshot_2 = MagicMock(spec=LiquidityGrabLifecycleSnapshot)
    mock_snapshot_2.snapshot_id = "s2"
    mock_snapshot_2.candidate_id = "c1"
    mock_snapshot_2.symbol_id = "BTC"
    mock_snapshot_2.summary = MagicMock()
    mock_snapshot_2.summary.state = LiquidityGrabLifecycleState.FAILED
    mock_snapshot_2.metadata = {"generated_at": "2023-01-02T00:00:00Z", "quality_report_id": "q1"}
    
    await repo.save(mock_snapshot_1)
    await repo.save(mock_snapshot_2)
    
    assert await repo.exists("s1") is True
    assert await repo.exists("s3") is False
    
    loaded = await repo.load("s1")
    assert loaded == mock_snapshot_1
    
    c1_snaps = await repo.query_by_candidate("c1")
    assert len(c1_snaps) == 2
    
    btc_snaps = await repo.query_by_symbol("BTC")
    assert len(btc_snaps) == 2
    
    failed_snaps = await repo.query_by_state(LiquidityGrabLifecycleState.FAILED)
    assert len(failed_snaps) == 1
    assert failed_snaps[0] == mock_snapshot_2
    
    q1_snaps = await repo.query_by_quality_report("q1")
    assert len(q1_snaps) == 2
    
    latest = await repo.load_latest("c1")
    assert latest == mock_snapshot_2
    
    assert await repo.load_latest("unknown") is None
