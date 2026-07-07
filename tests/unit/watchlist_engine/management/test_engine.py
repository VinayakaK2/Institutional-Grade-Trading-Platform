import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol, WatchlistCandidate, WatchlistSnapshot, WatchlistValidationStatus
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistStatus
from backend.watchlist_engine.management.engine import WatchlistManagementEngine

def create_mock_fresh_snapshot(version: int, candidates: list) -> FreshWatchlistSnapshot:
    base = WatchlistSnapshot(
        snapshot_id=str(uuid4()),
        version=version,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        symbol_count=len(candidates),
        candidates=candidates,
        metadata={},
        pipeline_version="1.0.0",
        config_hash="hash_value",
        validation_status=WatchlistValidationStatus.PASSED,
        source_universe_version=version
    )
    return FreshWatchlistSnapshot(
        freshness_snapshot_id=str(uuid4()),
        version=version,
        watchlist_snapshot=base,
        dataset_version="2026-07-07",
        parent_candidate_watchlist_version=str(version)
    )

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.load_latest_managed_snapshot.return_value = None
    return repo

@pytest.mark.asyncio
async def test_generate_managed_watchlist_success(mock_repository):
    engine = WatchlistManagementEngine(mock_repository)
    
    candidate = WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
            name="Apple Inc",
            sector="Tech"
        )
    )
    fresh_snapshot = create_mock_fresh_snapshot(1, [candidate])
    
    managed_snapshot = await engine.generate_managed_watchlist(fresh_snapshot)
    
    assert managed_snapshot is not None
    assert managed_snapshot.version == 1
    assert managed_snapshot.parent_fresh_watchlist_version == 1
    assert managed_snapshot.parent_candidate_watchlist_version == "1"
    assert managed_snapshot.dataset_version == "2026-07-07"
    assert managed_snapshot.status == WatchlistStatus.VALID
    
    # Verify deterministic business fingerprint was generated
    assert len(managed_snapshot.business_fingerprint) > 0
    
    # Verify repository was called
    mock_repository.save_managed_snapshot.assert_called_once()
    saved_snapshot, audit_record = mock_repository.save_managed_snapshot.call_args[0]
    
    assert saved_snapshot == managed_snapshot
    assert audit_record.event_type == "SNAPSHOT_CREATED"
    assert audit_record.metadata["business_fingerprint"] == managed_snapshot.business_fingerprint

@pytest.mark.asyncio
async def test_generate_managed_watchlist_increments_version(mock_repository):
    engine = WatchlistManagementEngine(mock_repository)
    
    # Setup mock to return an existing snapshot with version 5
    existing_snapshot = MagicMock()
    existing_snapshot.version = 5
    mock_repository.load_latest_managed_snapshot.return_value = existing_snapshot
    
    fresh_snapshot = create_mock_fresh_snapshot(1, [])
    managed_snapshot = await engine.generate_managed_watchlist(fresh_snapshot)
    
    assert managed_snapshot.version == 6
