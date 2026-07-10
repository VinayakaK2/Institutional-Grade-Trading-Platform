import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
from backend.trend_engine.optimization.models.models import BusinessFingerprint
from tests.unit.trend_engine.optimization.test_optimization_engine import mock_engine_setup
from backend.trend_engine.models.models import TrendSymbol, TrendDirection, TrendState
from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

from backend.trend_engine.optimization.engine.engine import TrendOptimizationEngine
from backend.trend_engine.optimization.config.config import TrendOptimizationConfig
from backend.trend_engine.optimization.repository.memory import InMemorySymbolTrendCache, InMemoryTrendOptimizationSnapshotRepository
from tests.unit.trend_engine.optimization.test_optimization_engine import (
    MockDetectionEngine, MockQualityEngine, MockLifecycleEngine,
    MockDetectionRepo, MockQualityRepo, MockLifecycleRepo
)
from backend.trend_engine.optimization.engine.parallel import AsyncBatchExecutor

async def run_benchmark():
    print("Initializing Benchmark Engine...")
    
    symbol_cache = InMemorySymbolTrendCache()
    snapshot_repo = InMemoryTrendOptimizationSnapshotRepository()
    config = TrendOptimizationConfig()
    executor = AsyncBatchExecutor()
    
    engine = TrendOptimizationEngine(
        config=config,
        detection_engine=MockDetectionEngine(),
        quality_engine=MockQualityEngine(),
        lifecycle_engine=MockLifecycleEngine(),
        detection_repo=MockDetectionRepo(),
        quality_repo=MockQualityRepo(),
        lifecycle_repo=MockLifecycleRepo(),
        symbol_cache=symbol_cache,
        snapshot_repo=snapshot_repo,
        parallel_executor=executor
    )
    
    def _create_ts(sym: str, exc: str):
        return TrendSymbol(
            watchlist_symbol=WatchlistSymbol(symbol=SymbolReference(symbol=sym, exchange=ExchangeReference(code=exc))),
            direction=TrendDirection.UPTREND,
            state=TrendState.VALID
        )

    # 500 Symbols
    symbols = [
        _create_ts(f"SYM{i}", "EXC")
        for i in range(500)
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
    
    print("\n--- RUN 1: Sequential Execution (Cold Cache) ---")
    engine._config = engine._config.model_copy(update={"is_parallel_enabled": False, "batch_size": 50})
    
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
    print(f"Execution Time: {opt_snap1.metrics.execution_duration_ms:.2f} ms")
    print(f"Reuse Rate: {opt_snap1.metrics.cache_hit_rate_percentage:.2f}%")
    
    # Clear Cache for Parallel test
    await symbol_cache.invalidate_fingerprint(fingerprint.compute_hash())
    
    print("\n--- RUN 2: Parallel Execution (Cold Cache) ---")
    engine._config = engine._config.model_copy(update={"is_parallel_enabled": True, "worker_count": 10, "batch_size": 50})
    
    opt_snap2 = await engine.run_optimized_pipeline(
        symbols=symbols,
        business_fingerprint=fingerprint,
        source_watchlist_snapshot_id="w1",
        source_watchlist_version=1,
        source_indicator_snapshot_id="i1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s1",
        source_structure_snapshot_version=1
    )
    print(f"Execution Time: {opt_snap2.metrics.execution_duration_ms:.2f} ms")
    print(f"Parallel Task Time: {opt_snap2.metrics.parallel_execution_time_ms:.2f} ms")
    print(f"Reuse Rate: {opt_snap2.metrics.cache_hit_rate_percentage:.2f}%")
    
    print("\n--- RUN 3: Parallel Execution (Hot Cache) ---")
    opt_snap3 = await engine.run_optimized_pipeline(
        symbols=symbols,
        business_fingerprint=fingerprint,
        source_watchlist_snapshot_id="w2", # Assuming new snapshot but same version
        source_watchlist_version=1,
        source_indicator_snapshot_id="i1",
        source_indicator_snapshot_version=1,
        source_structure_snapshot_id="s1",
        source_structure_snapshot_version=1
    )
    print(f"Execution Time: {opt_snap3.metrics.execution_duration_ms:.2f} ms")
    print(f"Parallel Task Time: {opt_snap3.metrics.parallel_execution_time_ms:.2f} ms")
    print(f"Reuse Rate: {opt_snap3.metrics.cache_hit_rate_percentage:.2f}%")
    
    print("\nBenchmark Complete.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
