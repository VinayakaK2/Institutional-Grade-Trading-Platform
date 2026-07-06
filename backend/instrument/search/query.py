"""
Search Query Engine
"""
from typing import List, Set
from backend.instrument.contracts.search import SearchCriteria, SearchEngineContract
from backend.instrument.search.index import SearchIndex
from backend.core.logger import get_logger

logger = get_logger("instrument.search.query")

class SearchQueryEngine(SearchEngineContract):
    """
    Executes search queries against a SearchIndex.
    """
    
    def __init__(self, index: SearchIndex):
        self._index = index
        
    def rebuild_index(self) -> None:
        """Contract requirement, but implementation might delegate differently."""
        logger.warning("Rebuild triggered via Query Engine contract.")
        # In reality, the manager rebuilds the index. This satisfies the contract if needed.

    def search(self, criteria: SearchCriteria) -> List[str]:
        """
        Executes a search and returns matching internal_ids.
        Applies intersection across all provided filters.
        """
        # If no criteria provided, return empty
        if not criteria.query and not criteria.exchange and not criteria.instrument_type:
            return []
            
        result_sets: List[Set[str]] = []
        
        # 1. Filter by Query (Symbol/ISIN/Name)
        if criteria.query:
            query_set = self._search_by_query(criteria.query, criteria.exact_match)
            if not query_set:
                return [] # Early exit if intersection will be empty
            result_sets.append(query_set)
            
        # 2. Filter by Exchange
        if criteria.exchange:
            ex_set = self._index.by_exchange.get(criteria.exchange.upper(), set())
            if not ex_set:
                return []
            result_sets.append(ex_set)
            
        # 3. Filter by Instrument Type
        if criteria.instrument_type:
            type_set = self._index.by_type.get(criteria.instrument_type.value, set())
            if not type_set:
                return []
            result_sets.append(type_set)
            
        # Intersect all active filters
        if not result_sets:
            return []
            
        final_set = set.intersection(*result_sets)
        
        # Validate that the IDs still exist in the main store (in case of lazy deletion)
        valid_ids = [iid for iid in final_set if iid in self._index.instruments]
        
        return valid_ids[:criteria.limit]
        
    def _search_by_query(self, query: str, exact_match: bool) -> Set[str]:
        """Handles text-based lookup (Symbol, ISIN, Name)."""
        query_upper = query.upper()
        query_lower = query.lower()
        
        # Always check exact symbol and ISIN
        exact_symbol = self._index.by_symbol.get(query_upper, set())
        exact_isin = self._index.by_isin.get(query_upper, set())
        
        results = exact_symbol.union(exact_isin)
        
        if not exact_match:
            # Add prefix matches
            # Split query in case user typed multiple words for name
            tokens = query_lower.split()
            
            if tokens:
                # Intersect prefixes for multiple tokens (e.g., "Apple Inc")
                prefix_results = []
                for token in tokens:
                    sym_prefix = self._index.prefix_symbol.get(token, set())
                    name_prefix = self._index.prefix_name.get(token, set())
                    combined_prefix = sym_prefix.union(name_prefix)
                    prefix_results.append(combined_prefix)
                    
                if prefix_results:
                    token_intersection = set.intersection(*prefix_results)
                    results = results.union(token_intersection)
                    
        return results
