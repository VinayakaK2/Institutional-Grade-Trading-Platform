from unittest.mock import AsyncMock, MagicMock
import pytest
from datetime import datetime, timezone
import hashlib

from backend.watchlist_engine.candidate_selection.engine import CandidateSelectionEngine
from backend.watchlist_engine.candidate_selection.config import CandidateSelectionSettings
from backend.universe_engine.contracts.query import ICandidateUniverseQueryService
from backend.watchlist_engine.contracts.contracts import IWatchlistEngine
from backend.universe_engine.models.read_views import CandidateUniverseView, CandidateUniverseSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.exceptions import WatchlistConfigurationError

@pytest.mark.asyncio
async def test_generate_candidate_watchlist() -> None:
    # Setup mocks
    mock_query = AsyncMock(spec=ICandidateUniverseQueryService)
    mock_engine = AsyncMock(spec=IWatchlistEngine)
    settings = CandidateSelectionSettings(candidate_limit=10, default_ordering="symbol_name")
    
    universe_view = CandidateUniverseView(
        universe_snapshot_id="u1",
        universe_version=1,
        pipeline_version="1.0.0",
        created_at=datetime.now(timezone.utc),
        symbols=[
            CandidateUniverseSymbol(
                symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
                exchange="EQUITY",
                instrument_type="EQUITY",
                is_active=True,
                is_certified=True
            )
        ]
    )
    
    mock_query.load_latest.return_value = universe_view
    
    # Run
    candidate_engine = CandidateSelectionEngine(mock_query, mock_engine, settings)
    await candidate_engine.generate_candidate_watchlist(run_id="run-1")
    
    # Assert query was called
    mock_query.load_latest.assert_called_once()
    
    # Assert engine was called
    mock_engine.generate_watchlist.assert_called_once()
    
    kwargs = mock_engine.generate_watchlist.call_args.kwargs
    assert kwargs["run_id"] == "run-1"
    assert kwargs["source_universe_snapshot_id"] == "u1"
    assert kwargs["source_universe_version"] == 1
    
    # Verify candidate mapping
    candidates = kwargs["candidates"]
    assert len(candidates) == 1
    assert candidates[0].watchlist_symbol.symbol.symbol == "AAPL"
    assert candidates[0].stage_metadata["is_active"] is True
    assert candidates[0].stage_metadata["is_certified"] is True

@pytest.mark.asyncio
async def test_generate_candidate_watchlist_no_universe() -> None:
    mock_query = AsyncMock(spec=ICandidateUniverseQueryService)
    mock_engine = AsyncMock(spec=IWatchlistEngine)
    settings = CandidateSelectionSettings()
    
    mock_query.load_latest.return_value = None
    
    candidate_engine = CandidateSelectionEngine(mock_query, mock_engine, settings)
    
    with pytest.raises(WatchlistConfigurationError, match="Failed to load CandidateUniverseView"):
        await candidate_engine.generate_candidate_watchlist(run_id="run-1")

@pytest.mark.asyncio
async def test_generate_candidate_watchlist_empty_universe() -> None:
    mock_query = AsyncMock(spec=ICandidateUniverseQueryService)
    mock_engine = AsyncMock(spec=IWatchlistEngine)
    settings = CandidateSelectionSettings()
    
    mock_query.load_latest.return_value = CandidateUniverseView(
        universe_snapshot_id="u1",
        universe_version=1,
        pipeline_version="1.0.0",
        created_at=datetime.now(timezone.utc),
        symbols=[]
    )
    
    candidate_engine = CandidateSelectionEngine(mock_query, mock_engine, settings)
    
    with pytest.raises(WatchlistConfigurationError, match="Loaded CandidateUniverseView is empty."):
        await candidate_engine.generate_candidate_watchlist(run_id="run-1")
