import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.quality.repository.memory import InMemoryQualityRepository
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityEnum

@pytest.mark.asyncio
async def test_in_memory_repository():
    repo = InMemoryQualityRepository()
    
    mock_report_1 = MagicMock()
    mock_report_1.report_id = "r1"
    mock_report_1.candidate_id = "c1"
    mock_report_1.symbol_id = "BTC"
    mock_report_1.classification.quality = LiquidityGrabQualityEnum.EXCELLENT
    mock_report_1.parent_trend_snapshot_version = 10
    mock_report_1.parent_consolidation_snapshot_version = 20
    
    mock_report_2 = MagicMock()
    mock_report_2.report_id = "r2"
    mock_report_2.candidate_id = "c2"
    mock_report_2.symbol_id = "ETH"
    mock_report_2.classification.quality = LiquidityGrabQualityEnum.POOR
    mock_report_2.parent_trend_snapshot_version = 10
    mock_report_2.parent_consolidation_snapshot_version = 21
    
    # Must have metadata timestamp for load_latest
    mock_report_1.metadata.created_timestamp = 100
    mock_report_2.metadata.created_timestamp = 200
    
    await repo.save(mock_report_1)
    await repo.save(mock_report_2)
    
    assert await repo.exists("r1") is True
    assert await repo.exists("r3") is False
    
    loaded = await repo.load("r1")
    assert loaded == mock_report_1
    
    c1_reports = await repo.query_by_candidate("c1")
    assert len(c1_reports) == 1
    assert c1_reports[0] == mock_report_1
    
    eth_reports = await repo.query_by_symbol("ETH")
    assert len(eth_reports) == 1
    assert eth_reports[0] == mock_report_2
    
    exc_reports = await repo.query_by_quality(LiquidityGrabQualityEnum.EXCELLENT)
    assert len(exc_reports) == 1
    assert exc_reports[0] == mock_report_1
    
    trend_reports = await repo.query_by_parent_trend_snapshot(10)
    assert len(trend_reports) == 2
    
    cons_reports = await repo.query_by_parent_consolidation_snapshot(20)
    assert len(cons_reports) == 1
    
    latest = await repo.load_latest()
    assert latest == mock_report_2
