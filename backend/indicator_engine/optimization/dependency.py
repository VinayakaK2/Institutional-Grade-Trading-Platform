from typing import List, Dict, Any, Optional
import logging
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType
from backend.indicator_engine.contracts.calculator import IndicatorCalculatorContract

logger = logging.getLogger(__name__)

class HardcodedDependencyOptimizer:
    """
    Optimizes specific hardcoded indicator dependencies to prevent duplicate mathematical calculations.
    For Phase 4.6, only EMA -> MACD optimization is implemented as requested.
    """
    
    @staticmethod
    def optimize_macd_dependencies(
        macd_calc: IndicatorCalculatorContract,
        ema_calc: IndicatorCalculatorContract,
        candles: List[Candle],
        dataset_version: str,
        macd_kwargs: Dict[str, Any],
        prev_state: Optional[Dict[str, Any]] = None
    ) -> List[IndicatorResult]:
        """
        Executes MACD by explicitly calculating the required EMAs first using the EMA calculator,
        and injecting the results into the MACD calculator.
        """
        fast_period = macd_kwargs.get("fast_period", 12)
        slow_period = macd_kwargs.get("slow_period", 26)
        
        
        # If we have a prev_state for MACD, it doesn't automatically mean we have it for EMA
        # In a generic system, we'd pull the EMA state from cache. For this specific hardcoded 
        # optimizer, we should ideally fetch the EMA previous state.
        # But if we don't have it explicitly, we must fallback to full recalc for the EMA parts, 
        # or we just rely on the fact that if MACD is cached, EMA should also be cached?
        # Actually, MACD state is not preserved right now, so prev_state is for MACD, not EMA.
        # If prev_state is passed, we can try to extract "fast_ema" and "slow_ema" if MACD stored it.
        # But wait, EMACalculator requires {"ema": value} as its previous state.
        # To avoid over-complicating the hardcoded optimizer, we can just do a full recalculation 
        # inside the optimizer if it's called. But wait, if new_candles is 1, a full recalc fails!
        # Thus, the caller (orchestrator) MUST pass the FULL candles list if we don't have the explicit EMA state!
        # Actually, we can fetch EMA state from the cache inside the orchestrator.
        fast_ema_results = ema_calc.calculate(candles, dataset_version, period=fast_period)
        slow_ema_results = ema_calc.calculate(candles, dataset_version, period=slow_period)
        
        def build_array(results, period, total_len):
            arr = [None] * (period - 1)
            # The results are from index period-1 to total_len-1
            arr.extend([r.value for r in results])
            # If for some reason the lengths don't match, pad with None
            while len(arr) < total_len:
                arr.append(None)
            return arr
            
        fast_emas_array = build_array(fast_ema_results, fast_period, len(candles))
        slow_emas_array = build_array(slow_ema_results, slow_period, len(candles))
        
        # Now execute MACD with the precalculated arrays
        macd_kwargs["precalculated_fast_emas"] = fast_emas_array
        macd_kwargs["precalculated_slow_emas"] = slow_emas_array
        
        macd_results = macd_calc.calculate(candles, dataset_version, **macd_kwargs)
        
        # Return both the EMAs (since they might be requested anyway) and the MACD results
        return fast_ema_results + slow_ema_results + macd_results

