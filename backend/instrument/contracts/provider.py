"""
Provider Contracts
"""
from typing import Protocol, List, AsyncGenerator
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata

class SymbolProviderContract(Protocol):
    """Abstract interface for external symbol data sources."""
    
    @property
    def name(self) -> str: ...
    
    async def fetch_exchanges(self) -> List[ExchangeMetadata]:
        """Fetch all supported exchanges."""
        ...
        
    def fetch_all_instruments(self) -> AsyncGenerator[List[Instrument], None]:
        """Fetch all instruments, yielding batches to prevent memory bloat."""
        ...
        
    def fetch_updates_since(self, version_id: str) -> AsyncGenerator[List[Instrument], None]:
        """Fetch only instruments that changed since a version (if supported)."""
        ...
