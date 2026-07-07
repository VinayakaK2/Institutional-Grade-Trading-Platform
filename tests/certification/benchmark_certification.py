import asyncio
import time
import os
import psutil
import platform
from typing import List
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle
from backend.indicator_engine.calculators.ema import EMACalculator
from backend.indicator_engine.calculators.macd import MACDCalculator
from backend.indicator_engine.optimization.cache import MemoryIndicatorCache
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.orchestrator import OptimizedIndicatorEngine
from tests.certification.utils import generate_alternating_candles

async def run_benchmark(symbol_count: int, candle_count: int = 100) -> str:
    print(f"\n--- Running Benchmark for {symbol_count} Symbols ({candle_count} candles each) ---")
    report_lines = [f"## Benchmark: {symbol_count} Symbols"]
    
    calculators = [EMACalculator(), MACDCalculator()]
    cache = MemoryIndicatorCache()
    metrics = OptimizationMetricsCollector()
    parallel = ParallelExecutionEngine(max_workers=None)
    opt_engine = OptimizedIndicatorEngine(calculators, cache, metrics, parallel)
    
    # Generate identical candle arrays but distinct symbols
    symbols_data = []
    base_candles = generate_alternating_candles(candle_count)
    for i in range(symbol_count):
        sym_candles = []
        sym = SymbolReference(symbol=f"SYM{i}", exchange=ExchangeReference(name="TEST", code="TEST"))
        for c in base_candles:
            sym_candles.append(Candle(
                symbol=sym, timeframe=c.timeframe, timestamp=c.timestamp,
                open=c.open, high=c.high, low=c.low, close=c.close, volume=c.volume
            ))
        symbols_data.append(sym_candles)
        
    start_time = time.time()
    
    # Parallel async execution
    tasks = [opt_engine.calculate_all_async(data, "v1") for data in symbols_data]
    opt_results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    total_indicators = sum(len(r) for r in opt_results)
    
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    
    m = metrics.get_metrics()
    
    report_lines.append(f"- **Execution Time:** {duration:.4f}s")
    report_lines.append(f"- **Total Indicators Generated:** {total_indicators}")
    report_lines.append(f"- **Throughput:** {m['throughput_symbols_per_sec']:.2f} symbols/sec")
    report_lines.append(f"- **Cache Hits:** {m['cache_hits']}")
    report_lines.append(f"- **Cache Misses:** {m['cache_misses']}")
    report_lines.append(f"- **Memory Usage (Process RSS):** {mem_mb:.2f} MB")
    
    parallel.shutdown()
    return "\n".join(report_lines)

async def main():
    import cpuinfo
    
    try:
        cpu_name = cpuinfo.get_cpu_info()['brand_raw']
    except Exception:
        cpu_name = platform.processor() or "Unknown CPU"

    reports = [
        "# Performance Certification Benchmark Report\n",
        "## Execution Environment",
        f"- **Operating System:** {platform.system()} {platform.release()}",
        f"- **Python Version:** {platform.python_version()}",
        f"- **CPU:** {cpu_name}\n"
    ]
    
    r100 = await run_benchmark(100)
    reports.append(r100)
    
    r500 = await run_benchmark(500)
    reports.append(r500)
    
    r1000 = await run_benchmark(1000)
    reports.append(r1000)
    
    final_report = "\n\n".join(reports)
    
    with open("docs/reports/certification/benchmark_report.md", "w") as f:
        f.write(final_report)
        
    print("Benchmark certification report saved to docs/reports/certification/benchmark_report.md")

if __name__ == "__main__":
    asyncio.run(main())
