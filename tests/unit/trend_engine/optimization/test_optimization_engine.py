import pytest
from datetime import datetime, timezone
from backend.trend_engine.optimization.engine.engine import TrendOptimizationEngine
from backend.trend_engine.optimization.config.config import TrendOptimizationConfig
from backend.trend_engine.optimization.models.models import BusinessFingerprint
from backend.trend_engine.optimization.repository.memory import (
    InMemoryTrendOptimizationSnapshotRepository,
    InMemorySymbolTrendCache
)
from backend.trend_engine.optimization.engine.parallel import AsyncBatchExecutor
from backend.trend_engine.models.models import TrendSymbol, TrendDirection, TrendState
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

# We will need some mock engines.
class MockDetectionEngine:
    async def generate_trend_snapshot(self, symbols, **kwargs):
        from backend.trend_engine.models.models import TrendSnapshot
        # Just return the same TrendSymbols
        for s in symbols:
            # We must use model_copy since they are frozen
            pass # We'll just reuse the input list for the mock
        return TrendSnapshot(
            snapshot_id="d1",
            snapshot_version=1,
            created_at=datetime.now(timezone.utc),
            source_watchlist_snapshot_id="w1",
            source_watchlist_version=1,
            source_indicator_snapshot_id="i1",
            source_indicator_snapshot_version=1,
            source_structure_snapshot_id="s1",
            source_structure_snapshot_version=1,
            symbols=symbols,
            pipeline_version="1.0",
            configuration_hash="h1",
            schema_version="1.0",
            execution_metadata={},
            audit_metadata={}
        )

class MockQualityEngine:
    async def evaluate_trend_quality(self, d_snap):
        from backend.trend_engine.quality.models.models import (
            TrendQualitySnapshot, TrendQualitySymbolResult, TrendQualityMetadata,
            TrendStrengthResult, TrendConsistencyResult, PullbackQualityResult,
            TrendPersistenceResult, NormalizedQualityMetrics
        )
        q_symbols = []
        for s in d_snap.symbols:
            # Need symbol_key, which isn't directly on TrendSymbol in my mock unless it's mock-provided
            # We'll get it from watchlist_symbol
            k = f"{s.watchlist_symbol.symbol.symbol}:{s.watchlist_symbol.symbol.exchange.code}" if hasattr(s, "watchlist_symbol") else getattr(s, "symbol_key", "UNKNOWN")
            q_symbols.append(TrendQualitySymbolResult(
                symbol_key=k,
                strength_metrics=TrendStrengthResult(ema_separation_ratio=1.0, direction_stability_percent=1.0, is_extended=False),
                consistency_metrics=TrendConsistencyResult(sequence_stability_ratio=1.0, structural_noise_percent=0.0, valid_structures_count=5),
                pullback_metrics=PullbackQualityResult(average_pullback_depth_percent=1.0, average_pullback_duration_bars=1.0, pullback_count=1, deepest_pullback_percent=2.0),
                persistence_metrics=TrendPersistenceResult(trend_age_bars=10, interruption_count=0, longest_uninterrupted_run_bars=10),
                normalized_metrics=NormalizedQualityMetrics(normalized_strength=1.0, normalized_consistency=1.0, normalized_pullback_quality=1.0, normalized_persistence=1.0)
            ))
        return TrendQualitySnapshot(
            quality_snapshot_id="q1",
            source_trend_snapshot_id=d_snap.snapshot_id,
            symbols=q_symbols,
            pipeline_version="1.0",
            quality_algorithm_version="1.0",
            configuration_hash="h1",
            metadata=TrendQualityMetadata(
                pipeline_version="1.0",
                configuration_hash="h1",
                configuration_version=1,
                quality_algorithm_version="1.0",
                evaluation_timestamp="2023-01-01T00:00:00Z",
                evaluation_duration_ms=10.0
            ),
            execution_metadata={},
            audit_metadata={}
        )

class MockLifecycleEngine:
    async def evaluate_lifecycle(self, d_snap, q_snap):
        from backend.trend_engine.lifecycle.models.models import TrendLifecycleSnapshot, TrendLifecycleSymbolResult, TrendLifecycleState, TrendLifecycleMetadata
        l_symbols = {}
        for s in d_snap.symbols:
            k = f"{s.watchlist_symbol.symbol.symbol}:{s.watchlist_symbol.symbol.exchange.code}"
            l_symbols[k] = TrendLifecycleSymbolResult(
                symbol_key=k,
                final_state=TrendLifecycleState.ACTIVE
            )
        return TrendLifecycleSnapshot(
            snapshot_id="l1",
            snapshot_version=1,
            parent_trend_snapshot_id=d_snap.snapshot_id,
            parent_trend_quality_snapshot_id=q_snap.quality_snapshot_id,
            symbols=l_symbols,
            pipeline_version="1.0",
            lifecycle_algorithm_version="1.0",
            lifecycle_rule_version=1,
            configuration_hash="h1",
            metadata=TrendLifecycleMetadata(),
            execution_metadata={},
            audit_metadata={}
        )

class MockDetectionRepo:
    async def save_snapshot(self, snap): pass
class MockQualityRepo:
    async def save_quality_snapshot(self, snap): pass
class MockLifecycleRepo:
    async def save_lifecycle_snapshot(self, snap): pass

@pytest.fixture
def mock_engine_setup():
    config = TrendOptimizationConfig(worker_count=2, batch_size=2)
    snapshot_repo = InMemoryTrendOptimizationSnapshotRepository()
    symbol_cache = InMemorySymbolTrendCache()
    parallel_executor = AsyncBatchExecutor()
    
    engine = TrendOptimizationEngine(
        config=config,
        detection_engine=MockDetectionEngine(),
        detection_repo=MockDetectionRepo(),
        quality_engine=MockQualityEngine(),
        quality_repo=MockQualityRepo(),
        lifecycle_engine=MockLifecycleEngine(),
        lifecycle_repo=MockLifecycleRepo(),
        snapshot_repo=snapshot_repo,
        symbol_cache=symbol_cache,
        parallel_executor=parallel_executor
    )
    return engine, symbol_cache, snapshot_repo

@pytest.mark.asyncio
async def test_optimization_engine_execution_and_caching(mock_engine_setup):
    engine, symbol_cache, snapshot_repo = mock_engine_setup
    
    def _create_ts(sym: str, exc: str):
        return TrendSymbol(
            watchlist_symbol=WatchlistSymbol(symbol=SymbolReference(symbol=sym, exchange=ExchangeReference(code=exc))),
            direction=TrendDirection.UPTREND,
            state=TrendState.VALID
        )

    symbols = [
        _create_ts("AAPL", "NASDAQ"),
        _create_ts("MSFT", "NASDAQ"),
        _create_ts("GOOGL", "NASDAQ")
    ]
    
    fingerprint = BusinessFingerprint(
        watchlist_snapshot_version=1,
        detection_algorithm_version="1.0",
        detection_config_hash="h1",
        quality_algorithm_version="1.0",
        quality_config_hash="h2",
        lifecycle_algorithm_version="1.0",
        lifecycle_rule_version=1,
        lifecycle_config_hash="h3",
        indicator_versions={"ema": "1.0"}
    )
    
    # Run 1: Cold Cache
    opt_snap1 = await engine.run_optimized_pipeline(
        symbols=symbols,
        business_fingerprint=fingerprint,
        source_watchlist_snapshot_id="w1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="i1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s1",
        source_structure_snapshot_version=1
    )
    
    assert opt_snap1.metrics.symbols_processed_total == 3
    assert opt_snap1.metrics.symbols_recomputed == 3
    assert opt_snap1.metrics.symbols_reused_from_cache == 0
    
    # Run 2: Hot Cache (100% reuse)
    opt_snap2 = await engine.run_optimized_pipeline(
        symbols=symbols,
        business_fingerprint=fingerprint,
        source_watchlist_snapshot_id="w2", # Note we can use a new watchlist snapshot, but version is same, or if version changes, fingerprint changes.
        # Assuming the fingerprint hasn't changed manually
        source_watchlist_version=1,
        source_indicator_snapshot_id="i1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s1",
        source_structure_snapshot_version=1
    )
    
    assert opt_snap2.metrics.symbols_processed_total == 3
    assert opt_snap2.metrics.symbols_recomputed == 0
    assert opt_snap2.metrics.symbols_reused_from_cache == 3
