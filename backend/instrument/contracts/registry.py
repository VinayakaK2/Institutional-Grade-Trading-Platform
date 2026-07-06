"""
Registry Contracts
"""
from typing import Protocol, List, Optional
from datetime import datetime
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata

class RegistrySnapshot(Protocol):
    """Represents a frozen state of the registry at a point in time."""
    version: int
    created_at: datetime
    
    def get_all_instruments(self) -> List[Instrument]: ...
    def get_all_exchanges(self) -> List[ExchangeMetadata]: ...

class RegistryManagerContract(Protocol):
    """Abstract definition of the registry manager."""
    
    async def get_instrument(self, internal_id: str) -> Optional[Instrument]: ...
    async def get_exchange(self, code: str) -> Optional[ExchangeMetadata]: ...
    
    async def load_initial(self) -> None: ...
    async def refresh_incremental(self) -> None: ...
    async def refresh_full(self) -> None: ...
    
    def get_snapshot(self) -> RegistrySnapshot: ...
