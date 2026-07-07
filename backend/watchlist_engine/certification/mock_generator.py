"""
Watchlist Certification Mock Dataset Generator
==============================================

Provides deterministic datasets for the certification framework.
"""
import random
from typing import List

from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.models import WatchlistSymbol, WatchlistCandidate

class MockDatasetGenerator:
    """
    Generates deterministic candidate datasets.
    """
    
    def __init__(self, seed: int = 42) -> None:
        self._seed = seed
        random.seed(self._seed)
        
    def _generate_symbol_reference(self, index: int) -> SymbolReference:
        return SymbolReference(
            symbol=f"TEST_{index}",
            exchange=ExchangeReference(code="NASDAQ")
        )
        
    def _generate_watchlist_symbol(self, index: int, market_segment: str = "US_EQUITY") -> WatchlistSymbol:
        return WatchlistSymbol(
            symbol=self._generate_symbol_reference(index),
            market_segment=market_segment,
            instrument_type="EQUITY",
            provider_metadata={"mocked": True}
        )
        
    def generate_candidates(self, scenario: str, size: int = 100) -> List[WatchlistCandidate]:
        """
        Generates candidates based on the specified scenario.
        
        Supported Scenarios:
        - empty_universe
        - single_symbol
        - duplicate_symbols
        - manual_include_only
        - manual_exclude_only
        - all_symbols_excluded
        - stale_market_data
        - missing_canonical_dataset
        - standard
        - max_size
        """
        # Ensure determinism by resetting seed before generation
        random.seed(f"{self._seed}_{scenario}_{size}")
        
        candidates: List[WatchlistCandidate] = []
        
        if scenario == "empty_universe":
            return []
            
        elif scenario == "single_symbol":
            symbol = self._generate_watchlist_symbol(1)
            candidates.append(WatchlistCandidate(watchlist_symbol=symbol))
            return candidates
            
        elif scenario == "duplicate_symbols":
            for i in range(size):
                # Only 10 unique symbols
                symbol = self._generate_watchlist_symbol((i % 10) + 1)
                candidates.append(WatchlistCandidate(watchlist_symbol=symbol))
            return candidates
            
        elif scenario == "manual_include_only":
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                cand = WatchlistCandidate(watchlist_symbol=symbol)
                cand.stage_metadata["manual_include"] = True
                candidates.append(cand)
            return candidates
            
        elif scenario == "manual_exclude_only":
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                cand = WatchlistCandidate(watchlist_symbol=symbol)
                cand.stage_metadata["manual_exclude"] = True
                candidates.append(cand)
            return candidates
            
        elif scenario == "all_symbols_excluded":
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                cand = WatchlistCandidate(watchlist_symbol=symbol)
                cand.stage_metadata["manual_exclude"] = True
                candidates.append(cand)
            return candidates
            
        elif scenario == "stale_market_data":
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                cand = WatchlistCandidate(watchlist_symbol=symbol)
                cand.stage_metadata["stale"] = True
                candidates.append(cand)
            return candidates
            
        elif scenario == "missing_canonical_dataset":
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                cand = WatchlistCandidate(watchlist_symbol=symbol)
                cand.stage_metadata["missing_canonical"] = True
                candidates.append(cand)
            return candidates
            
        else: # Standard and max_size fall through here
            for i in range(size):
                symbol = self._generate_watchlist_symbol(i)
                candidates.append(WatchlistCandidate(watchlist_symbol=symbol))
            return candidates
