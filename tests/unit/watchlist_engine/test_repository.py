"""
Unit tests for InMemoryWatchlistRepository.

Covers:
  - save_snapshot persists the snapshot.
  - load_snapshot returns the correct snapshot by ID.
  - load_snapshot returns None for an unknown ID.
  - load_latest_snapshot returns the most recent snapshot by created_at.
  - load_latest_snapshot returns None when the repository is empty.
  - load_snapshot_by_version returns the correct snapshot.
  - load_snapshot_by_version returns None for an unknown version.
  - list_snapshot_history returns snapshots ordered by version descending.
  - list_snapshot_history respects the limit parameter.
"""
import pytest
from datetime import datetime, timezone, timedelta

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import (
    WatchlistCandidate,
    WatchlistSnapshot,
    WatchlistSymbol,
    WatchlistValidationStatus,
)
from backend.watchlist_engine.repository.repository import InMemoryWatchlistRepository


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_candidate(ticker: str = "AAPL") -> WatchlistCandidate:
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol=ticker, exchange=ExchangeReference(code="NASDAQ")),
        )
    )


def make_snapshot(
    snapshot_id: str,
    version: int,
    offset_seconds: int = 0,
) -> WatchlistSnapshot:
    return WatchlistSnapshot(
        snapshot_id=snapshot_id,
        version=version,
        created_at=datetime.now(timezone.utc) + timedelta(seconds=offset_seconds),
        symbol_count=1,
        candidates=[make_candidate()],
        metadata={"run_id": f"run-{version}"},
        pipeline_version="1.0.0",
        config_hash="test_hash",
        validation_status=WatchlistValidationStatus.PASSED,
    )


# ── Save & Load ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_and_load_snapshot() -> None:
    """Saved snapshot should be retrievable by snapshot_id."""
    repo = InMemoryWatchlistRepository()
    snap = make_snapshot("snap-1", version=1)
    await repo.save_snapshot(snap)
    loaded = await repo.load_snapshot("snap-1")
    assert loaded is not None
    assert loaded.snapshot_id == "snap-1"
    assert loaded.version == 1


@pytest.mark.asyncio
async def test_load_snapshot_returns_none_for_unknown_id() -> None:
    """load_snapshot must return None when the snapshot_id does not exist."""
    repo = InMemoryWatchlistRepository()
    result = await repo.load_snapshot("nonexistent-id")
    assert result is None


# ── Latest Snapshot ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_load_latest_snapshot_empty_repo() -> None:
    """load_latest_snapshot must return None when the repository contains no snapshots."""
    repo = InMemoryWatchlistRepository()
    result = await repo.load_latest_snapshot()
    assert result is None


@pytest.mark.asyncio
async def test_load_latest_snapshot_returns_most_recent() -> None:
    """load_latest_snapshot must return the snapshot with the highest version number."""
    repo = InMemoryWatchlistRepository()
    await repo.save_snapshot(make_snapshot("snap-1", version=1, offset_seconds=0))
    await repo.save_snapshot(make_snapshot("snap-2", version=3, offset_seconds=5))   # Highest version
    await repo.save_snapshot(make_snapshot("snap-3", version=2, offset_seconds=10))  # Highest time, lower version

    latest = await repo.load_latest_snapshot()
    assert latest is not None
    # snap-2 has version=3 which is the highest — version is used for ordering.
    assert latest.snapshot_id == "snap-2"


# ── Version Lookup ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_load_snapshot_by_version() -> None:
    """load_snapshot_by_version must return the snapshot with the exact version."""
    repo = InMemoryWatchlistRepository()
    await repo.save_snapshot(make_snapshot("snap-1", version=1))
    await repo.save_snapshot(make_snapshot("snap-2", version=2))

    result = await repo.load_snapshot_by_version(2)
    assert result is not None
    assert result.snapshot_id == "snap-2"


@pytest.mark.asyncio
async def test_load_snapshot_by_version_returns_none_for_missing() -> None:
    """load_snapshot_by_version must return None for a version that does not exist."""
    repo = InMemoryWatchlistRepository()
    await repo.save_snapshot(make_snapshot("snap-1", version=1))

    result = await repo.load_snapshot_by_version(999)
    assert result is None


# ── Snapshot History ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_snapshot_history_ordered_by_version_descending() -> None:
    """list_snapshot_history must return snapshots ordered by version descending."""
    repo = InMemoryWatchlistRepository()
    for i in range(1, 6):
        await repo.save_snapshot(make_snapshot(f"snap-{i}", version=i))

    history = await repo.list_snapshot_history(limit=10)
    versions = [s.version for s in history]
    assert versions == [5, 4, 3, 2, 1]


@pytest.mark.asyncio
async def test_list_snapshot_history_respects_limit() -> None:
    """list_snapshot_history must not return more snapshots than the limit."""
    repo = InMemoryWatchlistRepository()
    for i in range(1, 6):
        await repo.save_snapshot(make_snapshot(f"snap-{i}", version=i))

    history = await repo.list_snapshot_history(limit=3)
    assert len(history) == 3
    # Must return the 3 most recent (highest version).
    assert history[0].version == 5
    assert history[1].version == 4
    assert history[2].version == 3
