import pytest
from typing import List
import asyncio
from datetime import datetime, timezone, timedelta
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorType, IndicatorResult
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.optimization.cache import MemoryIndicatorCache
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.incremental import IncrementalCalculationManager
from backend.indicator_engine.optimization.dependency import HardcodedDependencyOptimizer
from backend.indicator_engine.optimization.orchestrator import OptimizedIndicatorEngine

def create_candles(count: int, start_price: float = 100.0) -> List[Candle]:
    candles = []
    symbol = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="BINANCE", code="BINANCE"))
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for i in range(count):
        price = start_price + i
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H1,
            timestamp=base_time + timedelta(hours=i),
            open=price, high=price+1, low=price-1, close=price, volume=1000.0
        ))
    return candles

def test_memory_cache():
    cache = MemoryIndicatorCache()
    symbol = SymbolReference(symbol="BTC/USD", exchange=ExchangeReference(name="BINANCE", code="BINANCE"))
    tf = Timeframe.H1
    
    # Miss
    assert cache.get(symbol, tf, "v1", IndicatorType.EMA, "period=14") is None
    
    # Set
    res = IndicatorResult(
        symbol=symbol, timeframe=tf, dataset_version="v1", timestamp=datetime.now(timezone.utc),
        indicator_type=IndicatorType.EMA, parameters={}, value=100.0
    )
    cache.set(symbol, tf, "v1", IndicatorType.EMA, "period=14", [res])
    
    # Hit
    cached = cache.get(symbol, tf, "v1", IndicatorType.EMA, "period=14")
    assert cached is not None
    assert len(cached) == 1
    assert cached[0].value == 100.0
    
    # Invalidate
    cache.invalidate(symbol, tf, "v1", IndicatorType.EMA, "period=14")
    assert cache.get(symbol, tf, "v1", IndicatorType.EMA, "period=14") is None

def test_incremental_manager():
    candles = create_candles(50)
    symbol = candles[0].symbol
    
    # Scenario 1: No cache (Full recalculation)
    new_c, prev_state, valid = IncrementalCalculationManager.prepare_incremental_slice(candles, None)
    assert len(new_c) == 50
    assert prev_state is None
    assert len(valid) == 0
    
    # Scenario 2: Cache has exactly the first 25 candles
    cached_results = [
        IndicatorResult(
            symbol=symbol, timeframe=Timeframe.H1, dataset_version="v1", timestamp=candles[i].timestamp,
            indicator_type=IndicatorType.EMA, parameters={}, value=float(i), internal_state={"ema": float(i)}
        ) for i in range(25)
    ]
    
    new_c, prev_state, valid = IncrementalCalculationManager.prepare_incremental_slice(candles, cached_results)
    assert len(new_c) == 25
    assert prev_state == {"ema": 24.0}
    assert len(valid) == 25
    
    # Scenario 3: Gap detection
    cached_results = [
        IndicatorResult(
            symbol=symbol, timeframe=Timeframe.H1, dataset_version="v1", timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc),
            indicator_type=IndicatorType.EMA, parameters={}, value=0.0, internal_state=None
        )
    ]
    new_c, prev_state, valid = IncrementalCalculationManager.prepare_incremental_slice(candles, cached_results)
    # Gap detected, full recalc
    assert len(new_c) == 50
    assert prev_state is None
    assert len(valid) == 0

def test_dependency_optimizer():
    macd_calc = MACDCalculator()
    ema_calc = EMACalculator()
    candles = create_candles(50)
    
    results = HardcodedDependencyOptimizer.optimize_macd_dependencies(
        macd_calc, ema_calc, candles, "v1", {"fast_period": 12, "slow_period": 26, "signal_period": 9}
    )
    
    # It should return EMA12, EMA26, and MACD results
    types = [r.indicator_type for r in results]
    assert IndicatorType.EMA in types
    assert IndicatorType.MACD in types
    assert IndicatorType.MACD_SIGNAL in types
    assert IndicatorType.MACD_HISTOGRAM in types
    
    # Ensure values match regular MACD computation
    reg_macd = macd_calc.calculate(candles, "v1", fast_period=12, slow_period=26, signal_period=9)
    reg_macd_vals = [r.value for r in reg_macd if r.indicator_type == IndicatorType.MACD]
    opt_macd_vals = [r.value for r in results if r.indicator_type == IndicatorType.MACD]
    
    assert reg_macd_vals == opt_macd_vals

@pytest.mark.asyncio
async def test_parallel_execution():
    engine = ParallelExecutionEngine(max_workers=2)
    candles = create_candles(20)
    
    tasks = [
        (EMACalculator, candles, "v1", None, {"period": 14}),
        (EMACalculator, candles, "v1", None, {"period": 5})
    ]
    
    results = await engine.execute_batch(tasks)
    assert len(results) == 2
    assert len(results[0]) > 0
    assert len(results[1]) > 0
    engine.shutdown()

@pytest.mark.asyncio
async def test_orchestrator():
    calc = EMACalculator()
    cache = MemoryIndicatorCache()
    metrics = OptimizationMetricsCollector()
    parallel = ParallelExecutionEngine(max_workers=1)
    
    engine = OptimizedIndicatorEngine([calc], cache, metrics, parallel)
    candles = create_candles(30)
    
    # Run 1: Full
    results = await engine.calculate_all_async(candles, "v1")
    assert len(results) > 0
    m1 = metrics.get_metrics()
    assert m1["cache_misses"] == 1
    
    # Run 2: Incremental (Append 10 candles)
    candles_ext = create_candles(40)
    results_ext = await engine.calculate_all_async(candles_ext, "v1")
    assert len(results_ext) > len(results)
    
    m2 = metrics.get_metrics()
    assert m2["cache_hits"] == 1
    
    parallel.shutdown()
