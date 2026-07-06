"""
Search Contracts
"""
from typing import Protocol, List, Optional
from pydantic import BaseModel
from backend.instrument.models.instrument import InstrumentType

class SearchCriteria(BaseModel):
    """Filters for searching instruments."""
    query: Optional[str] = None
    exchange: Optional[str] = None
    instrument_type: Optional[InstrumentType] = None
    exact_match: bool = False
    limit: int = 50

class SearchEngineContract(Protocol):
    """Abstract interface for the search engine."""
    
    def search(self, criteria: SearchCriteria) -> List[str]:
        """Returns a list of internal_ids matching the criteria."""
        ...
        
    def rebuild_index(self) -> None:
        """Rebuilds the search index from the registry."""
        ...
