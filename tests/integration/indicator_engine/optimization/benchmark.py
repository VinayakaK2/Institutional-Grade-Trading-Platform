import asyncio
import time
from typing import List
from datetime import datetime, timezone, timedelta

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.indicator_engine.engine.engine import IndicatorEngine
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.optimization.cache import MemoryIndicatorCache
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.orchestrator import OptimizedIndicatorEngine

def create_mock_candles(symbol_id: str, count: int) -> List[Candle]:
    candles = []
    symbol = SymbolReference(symbol=symbol_id, exchange=ExchangeReference(name="BINANCE", code="BINANCE"))
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    price = 100.0
    for i in range(count):
        price += (i % 5) - 2
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H1,
            timestamp=base_time + timedelta(hours=i),
            open=price, high=price+1, low=price-1, close=price, volume=1000.0
        ))
    return candles

async def run_benchmark(symbol_count: int, candle_count: int = 100):
    print(f"\n--- Running Benchmark for {symbol_count} Symbols ({candle_count} candles each) ---")
    
    # 1. Setup
    calculators = [EMACalculator(), MACDCalculator()]
    
    base_engine = IndicatorEngine(calculators=calculators)
    
    cache = MemoryIndicatorCache()
    metrics = OptimizationMetricsCollector()
    parallel = ParallelExecutionEngine(max_workers=None) # Uses CPU count
    opt_engine = OptimizedIndicatorEngine(calculators, cache, metrics, parallel)
    
    symbols_data = [create_mock_candles(f"SYM{i}", candle_count) for i in range(symbol_count)]
    
    # 2. Baseline Run (Synchronous)
    start_time = time.time()
    base_total = 0
    for data in symbols_data:
        res = base_engine.calculate_all(data, "v1")
        base_total += len(res)
    base_duration = time.time() - start_time
    print(f"Baseline Engine Time:  {base_duration:.4f}s (Total Indicators: {base_total})")
    
    # 3. Optimized Run (Parallel + Dependency Optimizer)
    start_time = time.time()
    opt_total = 0
    
    # We execute them concurrently mimicking an async pipeline fan-out
    tasks = [opt_engine.calculate_all_async(data, "v1") for data in symbols_data]
    opt_results = await asyncio.gather(*tasks)
    
    for r in opt_results:
        opt_total += len(r)
        
    opt_duration = time.time() - start_time
    print(f"Optimized Engine Time: {opt_duration:.4f}s (Total Indicators: {opt_total})")
    print(f"Speedup Factor:        {base_duration / opt_duration:.2f}x")
    
    # 4. Incremental Run (Append 1 candle to all)
    print("\n--- Incremental Update (1 new candle) ---")
    
    incremental_data = []
    for i, data in enumerate(symbols_data):
        new_candle = Candle(
            symbol=data[0].symbol,
            timeframe=Timeframe.H1,
            timestamp=data[-1].timestamp + timedelta(hours=1),
            open=150, high=151, low=149, close=150, volume=1000
        )
        extended = data.copy()
        extended.append(new_candle)
        incremental_data.append(extended)
        
    start_time = time.time()
    tasks = [opt_engine.calculate_all_async(data, "v1") for data in incremental_data]
    await asyncio.gather(*tasks)
    incr_duration = time.time() - start_time
    
    print(f"Incremental Update Time: {incr_duration:.4f}s")
    
    m = metrics.get_metrics()
    print(f"Cache Hits: {m['cache_hits']} | Misses: {m['cache_misses']}")
    print(f"Throughput: {m['throughput_symbols_per_sec']:.2f} symbols/sec")
    
    parallel.shutdown()

async def main():
    await run_benchmark(100)
    await run_benchmark(500)
    await run_benchmark(1000)

if __name__ == "__main__":
    asyncio.run(main())
