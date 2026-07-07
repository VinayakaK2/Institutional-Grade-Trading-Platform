import pytest
import math
import asyncio
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.incremental import IncrementalCalculationManager
from backend.indicator_engine.optimization.cache import MemoryIndicatorCache
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector
from backend.indicator_engine.optimization.orchestrator import OptimizedIndicatorEngine
from backend.indicator_engine.engine.engine import IndicatorEngine

from tests.certification.utils import generate_alternating_candles, assert_floats_close

@pytest.mark.asyncio
async def test_long_running_incremental_drift():
    """
    Certifies that calculating 1000 candles incrementally (1 by 1) 
    does not introduce accumulating floating-point drift compared to calculating all 1000 at once.
    """
    candles = generate_alternating_candles(1000, start_price=100.0)
    
    calc = EMACalculator()
    base_engine = IndicatorEngine([calc])
    
    # Batch run
    batch_results = base_engine.calculate_all(candles, "v1")
    
    # Incremental run setup
    cache = MemoryIndicatorCache()
    metrics = OptimizationMetricsCollector()
    parallel = ParallelExecutionEngine(max_workers=1)
    opt_engine = OptimizedIndicatorEngine([calc], cache, metrics, parallel)
    
    # We will feed it chunks: first 100, then 1 by 1 for 900 candles
    await opt_engine.calculate_all_async(candles[:100], "v1")
    
    for i in range(101, 1001):
        await opt_engine.calculate_all_async(candles[:i], "v1")
        
    # Get final cached array by requesting the whole thing
    incremental_results = await opt_engine.calculate_all_async(candles, "v1")
    
    parallel.shutdown()
    
    assert len(batch_results) == len(incremental_results)
    
    # Check the final value for drift
    final_batch = batch_results[-1].value
    final_incr = incremental_results[-1].value
    
    assert_floats_close(final_batch, final_incr, msg="Incremental Drift on 1000 items")
