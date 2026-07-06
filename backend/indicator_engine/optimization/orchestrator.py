import time
import logging
from typing import List, Dict, Any, Type
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.contracts.calculator import IndicatorCalculatorContract
from backend.indicator_engine.engine.validation import IndicatorValidationEngine
from backend.indicator_engine.optimization.metrics import OptimizationMetricsCollector
from backend.indicator_engine.optimization.cache import IndicatorCacheContract
from backend.indicator_engine.optimization.incremental import IncrementalCalculationManager
from backend.indicator_engine.optimization.parallel import ParallelExecutionEngine
from backend.indicator_engine.optimization.dependency import HardcodedDependencyOptimizer

logger = logging.getLogger(__name__)

class OptimizedIndicatorEngine:
    """
    Wraps the standard Indicator Engine with optimization layers:
    - Incremental Calculation
    - In-Memory Caching
    - Parallel Execution
    - Hardcoded Dependency Optimization
    """
    def __init__(
        self,
        calculators: List[IndicatorCalculatorContract],
        cache: IndicatorCacheContract,
        metrics: OptimizationMetricsCollector,
        parallel_engine: ParallelExecutionEngine
    ):
        self._calculators = calculators
        self._cache = cache
        self._metrics = metrics
        self._parallel = parallel_engine
        
    async def calculate_all_async(
        self, 
        candles: List[Candle], 
        dataset_version: str
    ) -> List[IndicatorResult]:
        if not candles:
            return []
            
        start_time = time.time()
        
        # Validation (Fast)
        IndicatorValidationEngine.validate(candles)
        
        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        
        all_results = []
        parallel_tasks = []
        
        # 1. Dependency Resolution
        # Identify MACD calculators and EMA calculators if we have them
        macd_calcs = [c for c in self._calculators if c.indicator_type == IndicatorType.MACD]
        ema_calcs = [c for c in self._calculators if c.indicator_type == IndicatorType.EMA]
        
        macd_calc = macd_calcs[0] if macd_calcs else None
        ema_calc = ema_calcs[0] if ema_calcs else None
        
        for calc in self._calculators:
            # If MACD and we have EMA, it's handled via Dependency Optimizer natively.
            # But to keep parallel architecture clean, the Dependency Optimizer handles its own calculation 
            # synchronously or we can push it as a special parallel task.
            # For simplicity, if it's MACD, we run it explicitly via the Dependency Optimizer if EMA exists.
            
            # Param key extraction requires us to know the kwargs in advance.
            # Base engine just uses default kwargs. We assume default kwargs for caching.
            # Since calculators in this architecture don't declare params until `calculate()`, 
            # we will assume empty kwargs for the param_key or extract default from a dummy run.
            # A robust system would have the calculators expose `.get_default_params()`.
            # For this phase, we use an empty param_key since it's the only one used by default in `pipeline.py`.
            param_key = ""
            
            # Check Cache
            cached_results = self._cache.get(
                symbol, timeframe, dataset_version, calc.indicator_type, param_key
            )
            
            if cached_results:
                self._metrics.record_cache_hit(1)
            else:
                self._metrics.record_cache_miss(1)
                
            # Incremental Slice
            new_candles, prev_state, valid_cached = IncrementalCalculationManager.prepare_incremental_slice(
                candles, cached_results
            )
            
            all_results.extend(valid_cached)
            
            if not new_candles:
                continue
                
            if calc.indicator_type == IndicatorType.MACD and ema_calc:
                # Run through dependency optimizer synchronously for this symbol
                # MACD returns multiple indicator types, so we don't cache it easily as one type.
                # In this phase, we'll just run it.
                macd_results = HardcodedDependencyOptimizer.optimize_macd_dependencies(
                    macd_calc=calc,
                    ema_calc=ema_calc,
                    candles=new_candles,
                    dataset_version=dataset_version,
                    macd_kwargs={}
                )
                
                # Combine and Cache for each unique type returned
                unique_types = {r.indicator_type for r in macd_results}
                for ind_type in unique_types:
                    # Filter for this type
                    type_results = [r for r in macd_results if r.indicator_type == ind_type]
                    type_cached = [r for r in all_results if r.indicator_type == ind_type]
                    
                    full_results = type_cached + type_results
                    self._cache.set(symbol, timeframe, dataset_version, ind_type, "", full_results)
                
                all_results.extend(macd_results)
                continue
                
            if calc.indicator_type == IndicatorType.EMA and macd_calc:
                # EMA is handled inside the MACD dependency run above to prevent double calculation
                # (We skip running it independently if MACD is present).
                continue
                
            # Queue for parallel execution
            parallel_tasks.append((
                type(calc),
                new_candles,
                dataset_version,
                prev_state,
                {}
            ))
            
        # Execute Parallel Tasks
        if parallel_tasks:
            parallel_results_list = await self._parallel.execute_batch(parallel_tasks)
            
            # Reconstruct and Cache
            for i, p_results in enumerate(parallel_results_list):
                if not p_results:
                    continue
                
                # Combine with valid cached
                # Find the calc type to update cache
                # p_results[0].indicator_type
                ind_type = p_results[0].indicator_type
                
                # Get the cached portion for this specific type
                type_cached = [r for r in all_results if r.indicator_type == ind_type]
                full_results = type_cached + p_results
                
                self._cache.set(
                    symbol, timeframe, dataset_version, ind_type, "", full_results
                )
                
                all_results.extend(p_results)
                
        # Metrics
        end_time = time.time()
        exec_ms = (end_time - start_time) * 1000
        self._metrics.record_execution_time(exec_ms)
        self._metrics.record_batch_processed(1, len(all_results))
        
        return all_results
