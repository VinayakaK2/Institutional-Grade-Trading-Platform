import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol, WatchlistCandidate, WatchlistSnapshot, WatchlistValidationStatus
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistStatus
from backend.watchlist_engine.management.engine import WatchlistManagementEngine

def create_mock_fresh_snapshot(version: int, candidates: list, dataset_version: str = "2026-07-07", config_hash: str = "hash_value") -> FreshWatchlistSnapshot:
    base = WatchlistSnapshot(
        snapshot_id=str(uuid4()),
        version=version,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        symbol_count=len(candidates),
        candidates=candidates,
        metadata={},
        pipeline_version="1.0.0",
        config_hash=config_hash,
        validation_status=WatchlistValidationStatus.PASSED,
        source_universe_version=version
    )
    return FreshWatchlistSnapshot(
        freshness_snapshot_id=str(uuid4()),
        version=version,
        watchlist_snapshot=base,
        dataset_version=dataset_version,
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

@pytest.mark.asyncio
async def test_business_fingerprint_deterministic_generation(mock_repository):
    engine = WatchlistManagementEngine(mock_repository)
    
    # Create an initial set of candidates
    candidate1 = WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
            name="Apple Inc",
            sector="Tech"
        )
    )
    candidate2 = WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")),
            name="Microsoft Corp",
            sector="Tech"
        )
    )
    
    # Run 1
    fresh_snapshot_1 = create_mock_fresh_snapshot(1, [candidate1, candidate2], dataset_version="2026-07-07-A", config_hash="config_hash_abc")
    managed_snapshot_1 = await engine.generate_managed_watchlist(fresh_snapshot_1)
    
    # Run 2: Exact same candidates, dataset version, and config hash, but new underlying IDs
    fresh_snapshot_2 = create_mock_fresh_snapshot(2, [candidate2, candidate1], dataset_version="2026-07-07-A", config_hash="config_hash_abc") # Notice different order
    managed_snapshot_2 = await engine.generate_managed_watchlist(fresh_snapshot_2)
    
    # Verify deterministic business fingerprint
    assert managed_snapshot_1.business_fingerprint == managed_snapshot_2.business_fingerprint
    
    # Ensure they are conceptually identical except for audit fields (IDs, timestamps, managed version)
    assert managed_snapshot_1.fresh_watchlist_snapshot.watchlist_snapshot.symbol_count == managed_snapshot_2.fresh_watchlist_snapshot.watchlist_snapshot.symbol_count
    assert managed_snapshot_1.dataset_version == managed_snapshot_2.dataset_version
    assert managed_snapshot_1.config_hash == managed_snapshot_2.config_hash
    
    # Verify IDs are indeed different (proving they are two distinct objects in memory/audit)
    assert managed_snapshot_1.managed_snapshot_id != managed_snapshot_2.managed_snapshot_id
    assert managed_snapshot_1.created_at != managed_snapshot_2.created_at
