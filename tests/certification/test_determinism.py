import pytest
import asyncio
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.incremental import IncrementalCalculationManager
from backend.indicator_engine.engine.engine import IndicatorEngine
from backend.indicator_engine.optimization.orchestrator import OptimizedIndicatorEngine
from backend.indicator_engine.optimization.cache import MemoryIndicatorCache
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector

from tests.certification.utils import generate_alternating_candles, assert_floats_close

def test_single_vs_parallel_determinism():
    """Certifies that process-pool parallel calculations yield identical output to sequential calculations."""
    candles = generate_alternating_candles(50, start_price=100.0)
    calc = EMACalculator()
    
    # 1. Sequential Run
    seq_results = calc.calculate(candles, "v1", period=14)
    
    # 2. Parallel Run (Simulate directly)
    parallel = ParallelExecutionEngine(max_workers=2)
    loop = asyncio.get_event_loop()
    
    tasks = [
        (EMACalculator, candles, "v1", None, {"period": 14})
    ]
    
    par_results_list = loop.run_until_complete(parallel.execute_batch(tasks))
    par_results = par_results_list[0]
    
    parallel.shutdown()
    
    assert len(seq_results) == len(par_results)
    for s, p in zip(seq_results, par_results):
        assert_floats_close(s.value, p.value, msg=f"Sequential vs Parallel EMA mismatch at {s.timestamp}")

@pytest.mark.asyncio
async def test_batch_vs_incremental_determinism():
    """Certifies that incremental slice execution yields perfectly identical states and values to a full recalculation."""
    candles = generate_alternating_candles(100, start_price=100.0)
    
    calculators = [EMACalculator()]
    
    # Setup Optimized Engine
    cache = MemoryIndicatorCache()
    metrics = OptimizationMetricsCollector()
    parallel = ParallelExecutionEngine(max_workers=1)
    
    engine = OptimizedIndicatorEngine(calculators, cache, metrics, parallel)
    
    # 1. Full Batch (100 candles)
    # Since Optimized Engine caches implicitly, we run it on a separate instance or bypass cache.
    # Actually, we can just run standard engine for the batch reference.
    base_engine = IndicatorEngine(calculators)
    batch_results = base_engine.calculate_all(candles, "v1")
    
    # 2. Incremental (Run 99, then run 100)
    candles_99 = candles[:99]
    await engine.calculate_all_async(candles_99, "v1")
    
    # Run 100 (Incremental slice will hit)
    incremental_results = await engine.calculate_all_async(candles, "v1")
    
    parallel.shutdown()
    
    assert len(batch_results) == len(incremental_results)
    
    for b, i in zip(batch_results, incremental_results):
        assert_floats_close(b.value, i.value, msg=f"Batch vs Incremental EMA mismatch at {b.timestamp}")
