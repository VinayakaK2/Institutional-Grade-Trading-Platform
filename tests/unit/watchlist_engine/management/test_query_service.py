import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.watchlist_engine.management.query_service import ManagedWatchlistQueryService
from backend.watchlist_engine.management.models import WatchlistDiff, WatchlistDiffSummary

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def mock_diff_engine():
    return MagicMock()

@pytest.mark.asyncio
async def test_get_latest_snapshot(mock_repository, mock_diff_engine):
    service = ManagedWatchlistQueryService(mock_repository, mock_diff_engine)
    expected_snapshot = MagicMock()
    mock_repository.load_latest_managed_snapshot.return_value = expected_snapshot
    
    result = await service.get_latest_snapshot()
    
    assert result == expected_snapshot
    mock_repository.load_latest_managed_snapshot.assert_called_once()

@pytest.mark.asyncio
async def test_get_snapshot_diff(mock_repository, mock_diff_engine):
    service = ManagedWatchlistQueryService(mock_repository, mock_diff_engine)
    
    base_snapshot = MagicMock()
    base_snapshot.version = 1
    
    target_snapshot = MagicMock()
    target_snapshot.version = 2
    
    def side_effect(version):
        if version == 1:
            return base_snapshot
        if version == 2:
            return target_snapshot
        return None
        
    mock_repository.load_managed_snapshot_by_version.side_effect = side_effect
    
    expected_diff = WatchlistDiff(
        base_version=1,
        target_version=2,
        added_symbols=[],
        removed_symbols=[],
        unchanged_symbols=[],
        metadata_changes={},
        summary=WatchlistDiffSummary(added_count=0, removed_count=0, unchanged_count=0)
    )
    mock_diff_engine.compute_diff.return_value = expected_diff
    
    result = await service.get_snapshot_diff(1, 2)
    
    assert result == expected_diff
    mock_diff_engine.compute_diff.assert_called_once_with(target_snapshot, base_snapshot)
