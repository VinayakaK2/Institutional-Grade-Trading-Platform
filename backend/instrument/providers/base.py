"""
Base Provider Implementation
"""
from typing import List, AsyncGenerator
from backend.instrument.contracts.provider import SymbolProviderContract
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata
from backend.core.logger import get_logger

logger = get_logger("instrument.provider")

class BaseSymbolProvider(SymbolProviderContract):
    """
    Base implementation for symbol providers.
    Handles common logging and validation for providers.
    """
    
    def __init__(self, name: str):
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name

    async def fetch_exchanges(self) -> List[ExchangeMetadata]:
        raise NotImplementedError("Subclasses must implement fetch_exchanges")
        
    def fetch_all_instruments(self) -> AsyncGenerator[List[Instrument], None]:
        raise NotImplementedError("Subclasses must implement fetch_all_instruments")
        
    def fetch_updates_since(self, version_id: str) -> AsyncGenerator[List[Instrument], None]:
        raise NotImplementedError("Subclasses must implement fetch_updates_since")
