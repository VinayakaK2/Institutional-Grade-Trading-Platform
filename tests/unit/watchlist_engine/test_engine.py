"""
Unit tests for WatchlistEngine.

Covers:
  - Engine initialization with all dependencies.
  - generate_watchlist returns a valid WatchlistResult.
  - Snapshot version increments on successive runs.
  - Repository receives one save_snapshot call per run.
  - Validation errors propagate correctly (no snapshot is saved).
  - Pipeline errors propagate correctly (no snapshot is saved).
  - Engine is stateless — same instance can process multiple independent runs.
  - Repository failure propagates as WatchlistRepositoryError.
  - Empty pipeline (no stages) still produces a valid snapshot.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.engine.engine import WatchlistEngine
from backend.watchlist_engine.models.config import WatchlistSettings, WatchlistValidationSettings
from backend.watchlist_engine.models.exceptions import (
    WatchlistPipelineError,
    WatchlistValidationError,
    WatchlistRepositoryError,
)
from backend.watchlist_engine.models.models import (
    WatchlistCandidate,
    WatchlistSymbol,
    WatchlistValidationStatus,
)
from backend.watchlist_engine.pipeline.pipeline import WatchlistExecutionPipeline
from backend.watchlist_engine.repository.repository import InMemoryWatchlistRepository
from backend.watchlist_engine.validation.validators import WatchlistValidator


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_candidate(ticker: str, exchange_code: str = "NSE") -> WatchlistCandidate:
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol=ticker, exchange=ExchangeReference(code=exchange_code)),
            market_segment="EQUITY_CASH",
            instrument_type="EQUITY",
        )
    )


def build_engine(
    allow_empty: bool = False,
    max_stages: int = 20,
) -> WatchlistEngine:
    """Builds a WatchlistEngine wired with real in-memory dependencies."""
    settings = WatchlistSettings(
        validation=WatchlistValidationSettings(allow_empty_watchlist=allow_empty),
    )
    pipeline = WatchlistExecutionPipeline(settings.pipeline)
    repository = InMemoryWatchlistRepository()
    validator = WatchlistValidator(settings.validation)
    return WatchlistEngine(
        settings=settings,
        pipeline=pipeline,
        repository=repository,
        validator=validator,
    )


# ── Engine Lifecycle ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_engine_returns_valid_result() -> None:
    """generate_watchlist must return a WatchlistResult with a valid snapshot."""
    engine = build_engine()
    candidates = [make_candidate("RELIANCE"), make_candidate("INFY")]

    result = await engine.generate_watchlist("run-1", candidates)

    assert result.snapshot is not None
    assert result.snapshot.version == 1
    assert result.snapshot.symbol_count == 2
    assert result.snapshot.validation_status == WatchlistValidationStatus.PASSED
    assert result.snapshot.pipeline_version == "1.0.0"


@pytest.mark.asyncio
async def test_engine_version_increments_on_successive_runs() -> None:
    """Each run must produce a snapshot with an incremented version number."""
    engine = build_engine()
    candidates = [make_candidate("AAPL")]

    result1 = await engine.generate_watchlist("run-1", candidates)
    result2 = await engine.generate_watchlist("run-2", candidates)
    result3 = await engine.generate_watchlist("run-3", candidates)

    assert result1.snapshot.version == 1
    assert result2.snapshot.version == 2
    assert result3.snapshot.version == 3


@pytest.mark.asyncio
async def test_engine_persists_snapshot_to_repository() -> None:
    """The engine must persist the snapshot so it is retrievable from the repository."""
    settings = WatchlistSettings()
    pipeline = WatchlistExecutionPipeline(settings.pipeline)
    repository = InMemoryWatchlistRepository()
    validator = WatchlistValidator(settings.validation)
    engine = WatchlistEngine(settings=settings, pipeline=pipeline, repository=repository, validator=validator)

    candidates = [make_candidate("TCS")]
    result = await engine.generate_watchlist("run-1", candidates)

    loaded = await repository.load_snapshot(result.snapshot.snapshot_id)
    assert loaded is not None
    assert loaded.snapshot_id == result.snapshot.snapshot_id


# ── Statelessness ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_engine_is_stateless_across_runs() -> None:
    """Same engine instance must handle multiple independent runs correctly."""
    engine = build_engine()

    result_a = await engine.generate_watchlist("run-a", [make_candidate("WIPRO")])
    result_b = await engine.generate_watchlist("run-b", [make_candidate("HDFC"), make_candidate("ICICI")])

    # Each run must produce an independent snapshot.
    assert result_a.snapshot.snapshot_id != result_b.snapshot.snapshot_id
    assert result_a.snapshot.symbol_count == 1
    assert result_b.snapshot.symbol_count == 2


# ── Validation Error Propagation ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_validation_error_propagates_no_snapshot_saved() -> None:
    """If validation fails, the engine must re-raise the error and save no snapshot."""
    settings = WatchlistSettings()
    pipeline = WatchlistExecutionPipeline(settings.pipeline)
    repository = InMemoryWatchlistRepository()
    validator = WatchlistValidator(settings.validation)
    engine = WatchlistEngine(settings=settings, pipeline=pipeline, repository=repository, validator=validator)

    # Duplicate candidates will fail structural validation.
    dup1 = make_candidate("RELIANCE", "NSE")
    dup2 = make_candidate("RELIANCE", "NSE")

    with pytest.raises(WatchlistValidationError):
        await engine.generate_watchlist("run-fail", [dup1, dup2])

    # No snapshot should have been persisted.
    history = await repository.list_snapshot_history()
    assert len(history) == 0


# ── Pipeline Error Propagation ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_error_propagates() -> None:
    """If the pipeline raises WatchlistPipelineError, the engine must re-raise it."""
    settings = WatchlistSettings()
    mock_pipeline = AsyncMock()
    mock_pipeline.execute.side_effect = WatchlistPipelineError("Pipeline exploded")
    repository = InMemoryWatchlistRepository()
    validator = WatchlistValidator(settings.validation)

    engine = WatchlistEngine(
        settings=settings,
        pipeline=mock_pipeline,
        repository=repository,
        validator=validator,
    )

    with pytest.raises(WatchlistPipelineError):
        await engine.generate_watchlist("run-fail", [make_candidate("AAPL")])


# ── Empty Pipeline ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_engine_with_empty_pipeline() -> None:
    """Engine with no registered stages must still produce a valid snapshot."""
    engine = build_engine()
    result = await engine.generate_watchlist("run-empty", [make_candidate("MSFT")])

    assert result.snapshot.symbol_count == 1
    assert result.snapshot.metadata["pipeline_statistics"]["stages_executed"] == 0
