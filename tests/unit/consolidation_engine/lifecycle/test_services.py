import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from backend.consolidation_engine.lifecycle.services import ConsolidationLifecycleQueryService
from backend.consolidation_engine.lifecycle.models import ConsolidationLifecycleSnapshot, ConsolidationLifecycleState
from backend.consolidation_engine.lifecycle.contracts import IConsolidationLifecycleRepository

@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=IConsolidationLifecycleRepository)
    return repo

@pytest.fixture
def query_service(mock_repo):
    return ConsolidationLifecycleQueryService(repository=mock_repo)

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
async def test_latest_lifecycle_snapshot(query_service, mock_repo, sample_snapshot):
    mock_repo.load_latest.return_value = sample_snapshot
    result = await query_service.latest_lifecycle_snapshot("cand1")
    assert result == sample_snapshot
    mock_repo.load_latest.assert_called_once_with("cand1")

@pytest.mark.asyncio
async def test_historical_lifecycle_snapshots(query_service, mock_repo):
    # Currently stubbed to return empty
    result = await query_service.historical_lifecycle_snapshots("cand1")
    assert result == []

@pytest.mark.asyncio
async def test_active_consolidations(query_service, mock_repo, sample_snapshot):
    mock_repo.query_by_state.return_value = [sample_snapshot]
    result = await query_service.active_consolidations("AAPL")
    assert len(result) == 1
    assert result[0] == sample_snapshot
    
    result_none = await query_service.active_consolidations("MSFT")
    assert len(result_none) == 0

@pytest.mark.asyncio
async def test_broken_consolidations(query_service, mock_repo, sample_snapshot):
    broken_snap = sample_snapshot.model_copy(update={"lifecycle_state": ConsolidationLifecycleState.BROKEN})
    mock_repo.query_by_state.return_value = [broken_snap]
    result = await query_service.broken_consolidations()
    assert len(result) == 1
    
@pytest.mark.asyncio
async def test_ended_consolidations(query_service, mock_repo, sample_snapshot):
    ended_snap = sample_snapshot.model_copy(update={"lifecycle_state": ConsolidationLifecycleState.ENDED})
    mock_repo.query_by_state.return_value = [ended_snap]
    result = await query_service.ended_consolidations()
    assert len(result) == 1
