from typing import List, Tuple, Dict, Any, Optional
import logging
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult

logger = logging.getLogger(__name__)

class IncrementalCalculationManager:
    """
    Manages slicing of candles and state preservation for incremental calculations.
    """
    
    @staticmethod
    def prepare_incremental_slice(
        candles: List[Candle],
        cached_results: Optional[List[IndicatorResult]]
    ) -> Tuple[List[Candle], Optional[Dict[str, Any]], List[IndicatorResult]]:
        """
        Determines the new candles to calculate and the previous state to use.
        
        Returns:
            Tuple of:
            - List of new candles to calculate.
            - Previous state dictionary (or None if full recalculation).
            - List of valid cached results (to be prepended to the final list).
        """
        if not candles:
            return [], None, []
            
        if not cached_results:
            return candles, None, []
            
        # Get the latest cached result
        latest_result = cached_results[-1]
        
        # Verify the cache matches the candle stream up to latest_result.timestamp
        # If candles have been modified historically, a robust system would detect it.
        # For this phase, we assume append-only correctness if timestamps align.
        
        latest_timestamp = latest_result.timestamp
        
        # Find index of the first candle strictly AFTER the latest_timestamp
        slice_idx = 0
        for i, c in enumerate(candles):
            if c.timestamp > latest_timestamp:
                slice_idx = i
                break
            # If we reach the end and never break, it means no new candles.
            if i == len(candles) - 1 and c.timestamp <= latest_timestamp:
                slice_idx = len(candles)
                
        # If slice_idx is 0, it means the very first candle is newer than our cache,
        # or we somehow missed the overlapping history. In a pure append-only model,
        # this shouldn't happen unless the cache is completely stale/wrong.
        # If slice_idx == 0, we do a full recalculation to be safe, unless latest_timestamp < candles[0].timestamp
        
        if slice_idx == 0 and candles[0].timestamp > latest_timestamp:
             # Gap detected between cache and new candles, full recalculation required
             logger.warning(f"Gap detected between cache ({latest_timestamp}) and candles ({candles[0].timestamp}). Full recalc.")
             return candles, None, []
             
        if not latest_result.internal_state:
             # Calculator does not support incremental state preservation. Full recalc required.
             return candles, None, []
             
        new_candles = candles[slice_idx:]
        
        # Some indicators need the current and PREVIOUS candle price to calculate incrementally.
        # But wait, the calculator contract says: 
        # "If previous_state is provided, this list only needs to contain the minimal required candles for the next calculation step."
        # If the state captures EVERYTHING (e.g. current EMA value), passing just new_candles is fine.
        # But what if it's MACD? MACD state might have EMA12 and EMA26. 
        # What if it's RSI? RSI state needs average gain and average loss.
        # The base calculators we have (EMA, SMA) currently don't use the 'previous candle' price directly from the list, 
        # they just need the new prices.
        
        if not new_candles:
            return [], latest_result.internal_state, cached_results
            
        return new_candles, latest_result.internal_state, cached_results

