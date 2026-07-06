"""
Search Index Maintenance
"""
import collections
from typing import Dict, Set, Iterable
from backend.instrument.models.instrument import Instrument
from backend.core.logger import get_logger

logger = get_logger("instrument.search.index")

class SearchIndex:
    """
    In-memory inverted index for fast instrument lookups.
    Separates indexing responsibility from querying.
    """
    
    def __init__(self):
        # Maps internal_id to Instrument for direct retrieval
        self.instruments: Dict[str, Instrument] = {}
        
        # Exact match maps
        self.by_symbol: Dict[str, Set[str]] = collections.defaultdict(set)
        self.by_isin: Dict[str, Set[str]] = collections.defaultdict(set)
        self.by_exchange: Dict[str, Set[str]] = collections.defaultdict(set)
        self.by_type: Dict[str, Set[str]] = collections.defaultdict(set)
        
        # Prefix match maps (using lower-cased tokens)
        self.prefix_symbol: Dict[str, Set[str]] = collections.defaultdict(set)
        self.prefix_name: Dict[str, Set[str]] = collections.defaultdict(set)

    def _index_prefixes(self, text: str, internal_id: str, target_dict: Dict[str, Set[str]]):
        """Helper to index all prefixes of a tokenized string."""
        if not text:
            return
            
        tokens = text.lower().split()
        for token in tokens:
            for i in range(1, len(token) + 1):
                prefix = token[:i]
                target_dict[prefix].add(internal_id)
                
    def rebuild(self, instruments: Iterable[Instrument]) -> None:
        """
        Completely rebuilds the index from an iterable of instruments.
        """
        logger.info("Rebuilding search index")
        self.clear()
        
        for instr in instruments:
            self.add(instr)
            
        logger.info(f"Search index rebuilt with {len(self.instruments)} items")

    def clear(self) -> None:
        """Clears all indexing data."""
        self.instruments.clear()
        self.by_symbol.clear()
        self.by_isin.clear()
        self.by_exchange.clear()
        self.by_type.clear()
        self.prefix_symbol.clear()
        self.prefix_name.clear()
        
    def add(self, instrument: Instrument) -> None:
        """Adds a single instrument to the index."""
        iid = instrument.identity.internal_id
        
        # Base mapping
        self.instruments[iid] = instrument
        
        # Exact matching (case-insensitive keys)
        self.by_symbol[instrument.identity.symbol.upper()].add(iid)
        self.by_exchange[instrument.identity.exchange.upper()].add(iid)
        self.by_type[instrument.instrument_type.value].add(iid)
        
        if instrument.identity.isin:
            self.by_isin[instrument.identity.isin.upper()].add(iid)
            
        # Prefix matching
        self._index_prefixes(instrument.identity.symbol, iid, self.prefix_symbol)
        self._index_prefixes(instrument.metadata.name, iid, self.prefix_name)

    def remove(self, internal_id: str) -> None:
        """Removes a single instrument from the index.
        Note: Prefix removal is complex and might leak memory if not fully rebuilt.
        In practice, instruments are rarely deleted, just marked DELISTED.
        """
        if internal_id in self.instruments:
            del self.instruments[internal_id]
            # To properly clean inverted indices without full rebuild, 
            # we simply let the query engine filter out deleted IDs or handle it on rebuild.
