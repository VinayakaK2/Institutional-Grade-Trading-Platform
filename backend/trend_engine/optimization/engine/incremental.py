from typing import List, Tuple, Dict
import logging

from backend.trend_engine.optimization.models.models import SymbolPipelineResult
from backend.trend_engine.optimization.contracts.contracts import ISymbolTrendCache

logger = logging.getLogger(__name__)

class IncrementalProcessor:
    """
    Handles incremental processing logic by comparing incoming candidates 
    against the symbol cache using a deterministic fingerprint.
    """
    
    def __init__(self, cache: ISymbolTrendCache):
        self._cache = cache

    async def filter_candidates(
        self, 
        fingerprint_hash: str, 
        symbols: List[str]
    ) -> Tuple[List[str], Dict[str, SymbolPipelineResult]]:
        """
        Takes a list of symbol keys and checks the cache for an existing
        result matching the fingerprint hash.
        
        Returns:
            Tuple containing:
            1. List of symbol keys that need to be recomputed (cache miss).
            2. Dict of symbol_key -> SymbolPipelineResult for symbols reused from cache.
        """
        symbols_to_recompute: List[str] = []
        symbols_reused: Dict[str, SymbolPipelineResult] = {}
        
        for symbol in symbols:
            cached_result = await self._cache.get_cached_result(fingerprint_hash, symbol)
            if cached_result:
                symbols_reused[symbol] = cached_result
            else:
                symbols_to_recompute.append(symbol)
                
        return symbols_to_recompute, symbols_reused
