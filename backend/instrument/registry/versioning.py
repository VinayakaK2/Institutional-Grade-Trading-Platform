"""
Registry Versioning
"""
from datetime import datetime, timezone
from typing import List, Optional
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata
from pydantic import BaseModel, Field

class RegistrySnapshotModel(BaseModel):
    """
    Concrete implementation of the RegistrySnapshot contract.
    Contains the frozen state of the registry.
    """
    version: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    exchanges: List[ExchangeMetadata]
    instruments: List[Instrument]
    
    def get_all_instruments(self) -> List[Instrument]:
        return self.instruments
        
    def get_all_exchanges(self) -> List[ExchangeMetadata]:
        return self.exchanges

class VersionTracker:
    """
    Tracks the active version of the registry.
    """
    def __init__(self):
        self._current_version: int = 0
        self._last_updated: Optional[datetime] = None
        
    @property
    def current_version(self) -> int:
        return self._current_version
        
    @property
    def last_updated(self) -> Optional[datetime]:
        return self._last_updated
        
    def increment(self) -> int:
        """Increments the version and updates the timestamp."""
        self._current_version += 1
        self._last_updated = datetime.now(timezone.utc)
        return self._current_version
