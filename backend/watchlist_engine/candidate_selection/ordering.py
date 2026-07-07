"""
Ordering strategies for Candidate Selection.
Allows deterministic sorting based on configurable criteria.
"""
from abc import ABC, abstractmethod
from typing import List

from backend.watchlist_engine.models.models import WatchlistCandidate


class ICandidateOrderingStrategy(ABC):
    """
    Contract for candidate ordering strategies.
    Ensures deterministic ordering.
    """
    @abstractmethod
    def order(self, candidates: List[WatchlistCandidate]) -> List[WatchlistCandidate]:
        pass


class SymbolNameOrderingStrategy(ICandidateOrderingStrategy):
    """
    Orders WatchlistCandidates alphabetically by their symbol name.
    
    CRITICAL DETERMINISTIC ORDERING CONSTRAINT:
    If two symbols compare equal under the configured ordering strategy, 
    the secondary ordering must always be Symbol ID (or another immutable key). 
    This guarantees deterministic ordering even if duplicate display names exist.
    """
    def order(self, candidates: List[WatchlistCandidate]) -> List[WatchlistCandidate]:
        # We use a tuple for the sort key: (symbol_name, symbol_id)
        # to guarantee strict deterministic ordering.
        candidates.sort(key=lambda c: (
            c.watchlist_symbol.symbol.symbol, 
            c.watchlist_symbol.symbol.full_name
        ))
        return candidates


def get_ordering_strategy(strategy_name: str) -> ICandidateOrderingStrategy:
    """
    Factory for obtaining the configured ordering strategy.
    """
    if strategy_name == "symbol_name":
        return SymbolNameOrderingStrategy()
    
    # Default to symbol name if unknown, or raise. 
    # For now, default to symbol name to be safe.
    return SymbolNameOrderingStrategy()
