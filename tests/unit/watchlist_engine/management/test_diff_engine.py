import pytest
import datetime
from typing import List
from uuid import uuid4

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol, WatchlistCandidate, WatchlistSnapshot, WatchlistValidationStatus
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistStatus
from backend.watchlist_engine.management.diff_engine import SnapshotDiffEngine

def create_symbol(sym: str) -> WatchlistSymbol:
    return WatchlistSymbol(
        symbol=SymbolReference(symbol=sym, exchange=ExchangeReference(code="NASDAQ")),
        name=f"{sym} Inc",
        sector="Technology"
    )

def create_candidate(sym: str) -> WatchlistCandidate:
    return WatchlistCandidate(
        watchlist_symbol=create_symbol(sym)
    )

def create_managed_snapshot(version: int, symbols: List[str]) -> ManagedWatchlistSnapshot:
    candidates = [create_candidate(s) for s in symbols]
    base_snapshot = WatchlistSnapshot(
        snapshot_id=str(uuid4()),
        version=version,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        symbol_count=len(candidates),
        candidates=candidates,
        metadata={},
        pipeline_version="1.0.0",
        config_hash="abc",
        validation_status=WatchlistValidationStatus.PASSED,
        source_universe_version=1
    )
    fresh_snapshot = FreshWatchlistSnapshot(
        freshness_snapshot_id=str(uuid4()),
        version=version,
        watchlist_snapshot=base_snapshot,
        dataset_version="2026-07-07",
        parent_candidate_watchlist_version=str(version)
    )
    return ManagedWatchlistSnapshot(
        managed_snapshot_id=str(uuid4()),
        version=version,
        fresh_watchlist_snapshot=fresh_snapshot,
        parent_fresh_watchlist_version=version,
        parent_candidate_watchlist_version=str(version),
        parent_universe_version=1,
        dataset_version="2026-07-07",
        pipeline_version="1.0.0",
        config_hash="abc",
        business_fingerprint="fp",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        status=WatchlistStatus.VALID
    )

@pytest.fixture
def diff_engine():
    return SnapshotDiffEngine()

def test_compute_diff_no_base_snapshot(diff_engine):
    target = create_managed_snapshot(1, ["AAPL", "MSFT"])
    diff = diff_engine.compute_diff(target, base_snapshot=None)
    
    assert diff.base_version is None
    assert diff.target_version == 1
    assert diff.summary.added_count == 2
    assert diff.summary.removed_count == 0
    assert diff.summary.unchanged_count == 0
    assert len(diff.added_symbols) == 2
    assert {s.symbol.symbol for s in diff.added_symbols} == {"AAPL", "MSFT"}

def test_compute_diff_with_base_snapshot(diff_engine):
    base = create_managed_snapshot(1, ["AAPL", "MSFT", "GOOGL"])
    target = create_managed_snapshot(2, ["AAPL", "AMZN", "META"])
    
    diff = diff_engine.compute_diff(target, base_snapshot=base)
    
    assert diff.base_version == 1
    assert diff.target_version == 2
    assert diff.summary.added_count == 2
    assert diff.summary.removed_count == 2
    assert diff.summary.unchanged_count == 1
    
    assert {s.symbol.symbol for s in diff.added_symbols} == {"AMZN", "META"}
    assert {s.symbol.symbol for s in diff.removed_symbols} == {"MSFT", "GOOGL"}
    assert {s.symbol.symbol for s in diff.unchanged_symbols} == {"AAPL"}

def test_compute_diff_metadata_changes(diff_engine):
    base = create_managed_snapshot(1, ["AAPL"])
    target = create_managed_snapshot(2, ["AAPL"])
    
    # Modify dataset version to trigger metadata change
    target = target.model_copy(update={"dataset_version": "2026-07-08"})
    
    diff = diff_engine.compute_diff(target, base_snapshot=base)
    
    assert "dataset_version" in diff.metadata_changes
    assert diff.metadata_changes["dataset_version"]["from"] == "2026-07-07"
    assert diff.metadata_changes["dataset_version"]["to"] == "2026-07-08"
