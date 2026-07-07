"""
Unit tests for WatchlistEngine domain models.

Covers:
  - WatchlistSymbol construction and field defaults.
  - WatchlistCandidate construction and stage_metadata.
  - WatchlistStageResult immutability (frozen Pydantic model).
  - WatchlistExecutionContext mutability.
  - WatchlistSnapshot immutability (frozen Pydantic model).
  - WatchlistResult immutability.
"""
import pytest
from datetime import datetime, timezone

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import (
    WatchlistSymbol,
    WatchlistCandidate,
    WatchlistStageResult,
    WatchlistStageStatus,
    WatchlistExecutionContext,
    WatchlistSnapshot,
    WatchlistResult,
    WatchlistValidationStatus,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def symbol_ref() -> SymbolReference:
    """Standard SymbolReference for test usage."""
    return SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))


@pytest.fixture
def watchlist_symbol(symbol_ref: SymbolReference) -> WatchlistSymbol:
    """Standard WatchlistSymbol boundary model."""
    return WatchlistSymbol(
        symbol=symbol_ref,
        market_segment="EQUITY_CASH",
        instrument_type="EQUITY",
    )


@pytest.fixture
def candidate(watchlist_symbol: WatchlistSymbol) -> WatchlistCandidate:
    """Standard WatchlistCandidate."""
    return WatchlistCandidate(watchlist_symbol=watchlist_symbol)


# ── WatchlistSymbol ──────────────────────────────────────────────────────────

def test_watchlist_symbol_construction(symbol_ref: SymbolReference) -> None:
    """WatchlistSymbol should store all fields correctly."""
    ws = WatchlistSymbol(
        symbol=symbol_ref,
        market_segment="EQUITY_CASH",
        instrument_type="EQUITY",
        provider_metadata={"isin": "US0378331005"},
    )
    assert ws.symbol.symbol == "AAPL"
    assert ws.market_segment == "EQUITY_CASH"
    assert ws.instrument_type == "EQUITY"
    assert ws.provider_metadata == {"isin": "US0378331005"}


def test_watchlist_symbol_defaults(symbol_ref: SymbolReference) -> None:
    """WatchlistSymbol should apply sensible defaults for optional fields."""
    ws = WatchlistSymbol(symbol=symbol_ref)
    assert ws.market_segment == "UNKNOWN"
    assert ws.instrument_type == "UNKNOWN"
    assert ws.provider_metadata == {}


# ── WatchlistCandidate ───────────────────────────────────────────────────────

def test_watchlist_candidate_construction(watchlist_symbol: WatchlistSymbol) -> None:
    """WatchlistCandidate should wrap WatchlistSymbol correctly."""
    candidate = WatchlistCandidate(watchlist_symbol=watchlist_symbol)
    assert candidate.watchlist_symbol is watchlist_symbol
    assert candidate.stage_metadata == {}


def test_watchlist_candidate_stage_metadata_mutation(candidate: WatchlistCandidate) -> None:
    """stage_metadata must be mutable — stages write to it during pipeline execution."""
    candidate.stage_metadata["test_key"] = "test_value"
    assert candidate.stage_metadata["test_key"] == "test_value"


# ── WatchlistStageResult ─────────────────────────────────────────────────────

def test_stage_result_is_frozen() -> None:
    """WatchlistStageResult must be immutable after construction."""
    result = WatchlistStageResult(
        stage_name="TestStage",
        status=WatchlistStageStatus.SUCCESS,
        duration_ms=12.5,
    )
    with pytest.raises(Exception):
        result.stage_name = "Mutated"  # type: ignore[misc]


def test_stage_result_defaults() -> None:
    """WatchlistStageResult should default metadata and warnings to empty collections."""
    result = WatchlistStageResult(
        stage_name="TestStage",
        status=WatchlistStageStatus.SUCCESS,
        duration_ms=5.0,
    )
    assert result.metadata == {}
    assert result.warnings == []


# ── WatchlistExecutionContext ─────────────────────────────────────────────────

def test_execution_context_is_mutable(candidate: WatchlistCandidate) -> None:
    """WatchlistExecutionContext must be mutable so stages can accumulate results."""
    ctx = WatchlistExecutionContext(
        run_id="run-1",
        snapshot_id="snap-1",
        started_at=datetime.now(timezone.utc),
        candidates=[candidate],
    )
    # Verify mutability.
    ctx.shared_state["key"] = "value"
    assert ctx.shared_state["key"] == "value"

    new_result = WatchlistStageResult(
        stage_name="Stage1",
        status=WatchlistStageStatus.SUCCESS,
        duration_ms=1.0,
    )
    ctx.stage_results.append(new_result)
    assert len(ctx.stage_results) == 1


# ── WatchlistSnapshot ─────────────────────────────────────────────────────────

def test_watchlist_snapshot_is_frozen(candidate: WatchlistCandidate) -> None:
    """WatchlistSnapshot must be immutable after construction."""
    snap = WatchlistSnapshot(
        snapshot_id="snap-1",
        version=1,
        created_at=datetime.now(timezone.utc),
        symbol_count=1,
        candidates=[candidate],
        metadata={"run_id": "run-1"},
        pipeline_version="1.0.0",
        config_hash="test_hash",
        validation_status=WatchlistValidationStatus.PASSED,
    )
    with pytest.raises(Exception):
        snap.version = 99  # type: ignore[misc]


def test_watchlist_snapshot_defaults(candidate: WatchlistCandidate) -> None:
    """WatchlistSnapshot.source_pipeline_version should default to None."""
    snap = WatchlistSnapshot(
        snapshot_id="snap-1",
        version=1,
        created_at=datetime.now(timezone.utc),
        symbol_count=1,
        candidates=[candidate],
        metadata={},
        pipeline_version="1.0.0",
        config_hash="test_hash",
        validation_status=WatchlistValidationStatus.PASSED,
    )
    assert snap.source_pipeline_version is None


# ── WatchlistResult ────────────────────────────────────────────────────────────

def test_watchlist_result_is_frozen(candidate: WatchlistCandidate) -> None:
    """WatchlistResult must be immutable."""
    snap = WatchlistSnapshot(
        snapshot_id="snap-1",
        version=1,
        created_at=datetime.now(timezone.utc),
        symbol_count=1,
        candidates=[candidate],
        metadata={},
        pipeline_version="1.0.0",
        config_hash="test_hash",
        validation_status=WatchlistValidationStatus.PASSED,
    )
    result = WatchlistResult(snapshot=snap)
    with pytest.raises(Exception):
        result.snapshot = snap  # type: ignore[misc]
