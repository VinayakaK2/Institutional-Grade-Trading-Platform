import pytest
import datetime
from unittest.mock import AsyncMock

from backend.watchlist_engine.models.models import (
    WatchlistCandidate, WatchlistSymbol, WatchlistExecutionContext, 
    WatchlistSnapshot, WatchlistStageResult, WatchlistStageStatus,
    WatchlistResult
)
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.optimization.fingerprint import OptimizationFingerprintBuilder
from backend.watchlist_engine.optimization.pipeline import OptimizedWatchlistPipeline
from backend.watchlist_engine.optimization.engine import WatchlistOptimizationEngine
from backend.watchlist_engine.models.config import WatchlistOptimizationSettings


@pytest.fixture
def candidate_1():
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="US")),
            market_segment="US",
            is_certified=True
        )
    )

@pytest.fixture
def candidate_2():
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="US")),
            market_segment="US",
            is_certified=True
        )
    )

def test_fingerprint_builder_is_deterministic(candidate_1, candidate_2):
    f1 = OptimizationFingerprintBuilder.build("v1", "hash1", [candidate_1, candidate_2])
    f2 = OptimizationFingerprintBuilder.build("v1", "hash1", [candidate_2, candidate_1])
    # Different order of candidates should yield same fingerprint because it sorts internally
    assert f1 == f2
    
    f3 = OptimizationFingerprintBuilder.build("v1", "hash2", [candidate_1, candidate_2])
    assert f1 != f3

@pytest.mark.asyncio
async def test_optimized_pipeline_full_recalc(candidate_1, candidate_2):
    mock_inner_pipeline = AsyncMock()
    
    # Inner pipeline returns context with some dummy stage results
    def mock_execute(ctx):
        ctx.stage_results = [
            WatchlistStageResult(stage_name="TestStage", status=WatchlistStageStatus.SUCCESS, duration_ms=10.0)
        ]
        return ctx
        
    mock_inner_pipeline.execute.side_effect = mock_execute
    
    mock_repository = AsyncMock()
    mock_repository.load_latest_snapshot.return_value = None
    
    settings = WatchlistOptimizationSettings(
        enable_incremental_processing=True,
        enable_parallel_execution=False
    )
    
    pipeline = OptimizedWatchlistPipeline(mock_inner_pipeline, settings, mock_repository)
    
    now = datetime.datetime.now(datetime.timezone.utc)
    ctx = WatchlistExecutionContext(
        run_id="run1",
        snapshot_id="snap1",
        started_at=now,
        candidates=[candidate_1, candidate_2],
        metadata={"config_hash": "hash1"}
    )
    
    res = await pipeline.execute(ctx)
    
    assert len(res.candidates) == 2
    assert "optimization_stats" in res.metadata
    assert res.metadata["optimization_stats"]["reused_candidates"] == 0
    assert res.metadata["optimization_stats"]["processed_candidates"] == 2
    
    assert "optimization_fingerprint" in res.metadata
    assert len(res.stage_results) == 1
    assert res.stage_results[0].metadata["optimization"]["processed_candidates"] == 2
    
    mock_inner_pipeline.execute.assert_called_once()

@pytest.mark.asyncio
async def test_optimized_pipeline_incremental_reuse(candidate_1, candidate_2):
    mock_inner_pipeline = AsyncMock()
    
    def mock_execute(ctx):
        ctx.stage_results = [
            WatchlistStageResult(stage_name="TestStage", status=WatchlistStageStatus.SUCCESS, duration_ms=10.0)
        ]
        return ctx
        
    mock_inner_pipeline.execute.side_effect = mock_execute
    
    mock_repository = AsyncMock()
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Previous snapshot only had candidate_1
    prev_snapshot = WatchlistSnapshot(
        snapshot_id="snap0",
        version=1,
        created_at=now,
        symbol_count=1,
        pipeline_version="1.0.0",
        config_hash="hash1",
        validation_status="PASSED",
        candidates=[candidate_1],
        metadata={}
    )
    mock_repository.load_latest_snapshot.return_value = prev_snapshot
    
    settings = WatchlistOptimizationSettings(
        enable_incremental_processing=True,
        enable_parallel_execution=False
    )
    
    pipeline = OptimizedWatchlistPipeline(mock_inner_pipeline, settings, mock_repository)
    
    ctx = WatchlistExecutionContext(
        run_id="run1",
        snapshot_id="snap1",
        started_at=now,
        candidates=[candidate_1, candidate_2],
        metadata={"config_hash": "hash1"}
    )
    
    res = await pipeline.execute(ctx)
    
    assert len(res.candidates) == 2
    assert res.metadata["optimization_stats"]["reused_candidates"] == 1
    assert res.metadata["optimization_stats"]["processed_candidates"] == 1
    
    assert len(res.stage_results) == 1
    assert res.stage_results[0].metadata["optimization"]["processed_candidates"] == 1
    assert res.stage_results[0].metadata["optimization"]["reused_candidates"] == 1
    
    # Inner pipeline should have been called with ONLY candidate_2
    called_ctx = mock_inner_pipeline.execute.call_args[0][0]
    assert len(called_ctx.candidates) == 1
    assert called_ctx.candidates[0].watchlist_symbol.symbol.symbol == "MSFT"

@pytest.mark.asyncio
async def test_watchist_optimization_engine_bypass(candidate_1):
    mock_inner_engine = AsyncMock()
    mock_repository = AsyncMock()
    
    settings = WatchlistOptimizationSettings(enable_incremental_processing=True)
    engine = WatchlistOptimizationEngine(mock_inner_engine, settings, mock_repository)
    
    # Pre-calculate fingerprint
    fp = OptimizationFingerprintBuilder.build("n/a", "hash1", [candidate_1])
    
    now = datetime.datetime.now(datetime.timezone.utc)
    prev_snapshot = WatchlistSnapshot(
        snapshot_id="snap0",
        version=1,
        created_at=now,
        symbol_count=1,
        pipeline_version="1.0.0",
        config_hash="hash1",
        validation_status="PASSED",
        candidates=[candidate_1],
        metadata={"optimization_fingerprint": fp}
    )
    
    mock_repository.load_latest_snapshot.return_value = prev_snapshot
    
    res = await engine.generate_watchlist(
        run_id="run2",
        candidates=[candidate_1],
        config_hash="hash1"
    )
    
    assert res.snapshot == prev_snapshot
    mock_inner_engine.generate_watchlist.assert_not_called()

@pytest.mark.asyncio
async def test_watchist_optimization_engine_no_bypass(candidate_1, candidate_2):
    mock_inner_engine = AsyncMock()
    mock_repository = AsyncMock()
    
    settings = WatchlistOptimizationSettings(enable_incremental_processing=True)
    engine = WatchlistOptimizationEngine(mock_inner_engine, settings, mock_repository)
    
    # Pre-calculate fingerprint for just candidate_1
    fp = OptimizationFingerprintBuilder.build("n/a", "hash1", [candidate_1])
    
    now = datetime.datetime.now(datetime.timezone.utc)
    prev_snapshot = WatchlistSnapshot(
        snapshot_id="snap0",
        version=1,
        created_at=now,
        symbol_count=1,
        pipeline_version="1.0.0",
        config_hash="hash1",
        validation_status="PASSED",
        candidates=[candidate_1],
        metadata={"optimization_fingerprint": fp}
    )
    
    mock_repository.load_latest_snapshot.return_value = prev_snapshot
    
    # We pass BOTH candidate_1 and candidate_2, so fingerprint won't match
    await engine.generate_watchlist(
        run_id="run2",
        candidates=[candidate_1, candidate_2],
        config_hash="hash1"
    )
    
    mock_inner_engine.generate_watchlist.assert_called_once()
