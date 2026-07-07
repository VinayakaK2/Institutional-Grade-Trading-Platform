import pytest
import datetime
from unittest.mock import AsyncMock

from backend.watchlist_engine.engine.engine import WatchlistEngine
from backend.watchlist_engine.models.models import WatchlistSnapshot, WatchlistCandidate, WatchlistSymbol, WatchlistResult
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.freshness.engine import FreshnessEngine
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot

@pytest.fixture
def candidate_symbol():
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")),
            market_segment="US",
            is_certified=True
        ),
        metadata={}
    )

@pytest.fixture
def watchlist_snapshot(candidate_symbol):
    now = datetime.datetime.now(datetime.timezone.utc)
    return WatchlistSnapshot(
        snapshot_id="test-snapshot",
        version=1,
        created_at=now,
        symbol_count=1,
        source_universe_version=1,
        pipeline_version="p1",
        candidate_selection_version="v1.0.0",
        config_hash="hash",
        validation_status="PASSED",
        candidates=[candidate_symbol],
        metadata={}
    )

@pytest.mark.asyncio
async def test_freshness_engine_generates_fresh_snapshot(watchlist_snapshot, candidate_symbol):
    mock_watchlist_engine = AsyncMock(spec=WatchlistEngine)
    mock_repository = AsyncMock()
    
    # Inner engine returns a WatchlistResult with a snapshot
    now = datetime.datetime.now(datetime.timezone.utc)
    inner_snapshot = WatchlistSnapshot(
        snapshot_id="inner-snapshot",
        version=2,
        created_at=now,
        symbol_count=1,
        source_universe_version=1,
        pipeline_version="p1",
        config_hash="hash",
        validation_status="PASSED",
        candidates=[candidate_symbol],
        metadata={}
    )
    mock_watchlist_engine.generate_watchlist.return_value = WatchlistResult(
        snapshot=inner_snapshot
    )
    
    # Repository has no prior snapshots (version 1)
    mock_repository.load_latest_fresh_snapshot.return_value = None
    
    engine = FreshnessEngine(
        watchlist_engine=mock_watchlist_engine,
        freshness_repository=mock_repository,
        dataset_version="v2.0.0"
    )
    
    result = await engine.generate_fresh_watchlist(watchlist_snapshot)
    
    assert isinstance(result, FreshWatchlistSnapshot)
    assert result.version == 1
    assert result.dataset_version == "v2.0.0"
    assert result.parent_candidate_watchlist_version == "v1.0.0"
    assert result.watchlist_snapshot == inner_snapshot
    
    mock_watchlist_engine.generate_watchlist.assert_called_once()
    kwargs = mock_watchlist_engine.generate_watchlist.call_args[1]
    assert kwargs["candidates"] == watchlist_snapshot.candidates
    assert kwargs["config_hash"] == "freshness_v2.0.0"
    assert kwargs["candidate_selection_version"] == "v1.0.0"
    mock_repository.save_fresh_snapshot.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_freshness_engine_is_deterministic(watchlist_snapshot, candidate_symbol):
    mock_watchlist_engine = AsyncMock(spec=WatchlistEngine)
    mock_repository = AsyncMock()
    
    # Inner engine returns a deterministic WatchlistResult
    now = datetime.datetime.now(datetime.timezone.utc)
    inner_snapshot = WatchlistSnapshot(
        snapshot_id="inner-snapshot",
        version=2,
        created_at=now,
        symbol_count=1,
        source_universe_version=1,
        pipeline_version="p1",
        config_hash="hash",
        validation_status="PASSED",
        candidates=[candidate_symbol],
        metadata={}
    )
    mock_watchlist_engine.generate_watchlist.return_value = WatchlistResult(
        snapshot=inner_snapshot
    )
    
    mock_repository.load_latest_fresh_snapshot.return_value = None
    
    engine1 = FreshnessEngine(
        watchlist_engine=mock_watchlist_engine,
        freshness_repository=mock_repository,
        dataset_version="v2.0.0"
    )
    result1 = await engine1.generate_fresh_watchlist(watchlist_snapshot)
    
    # Run again with same config
    engine2 = FreshnessEngine(
        watchlist_engine=mock_watchlist_engine,
        freshness_repository=mock_repository,
        dataset_version="v2.0.0"
    )
    result2 = await engine2.generate_fresh_watchlist(watchlist_snapshot)
    
    # Verify deterministic behavior
    assert result1.dataset_version == result2.dataset_version
    assert result1.parent_candidate_watchlist_version == result2.parent_candidate_watchlist_version
    assert result1.watchlist_snapshot == result2.watchlist_snapshot
