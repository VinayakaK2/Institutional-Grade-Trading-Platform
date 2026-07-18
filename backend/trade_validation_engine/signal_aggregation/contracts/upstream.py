from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

TSnapshot = TypeVar('TSnapshot')

class IReadOnlySnapshotQueryService(ABC, Generic[TSnapshot]):
    """
    Generic read-only query service contract for upstream dependencies.
    """
    @abstractmethod
    async def get_by_snapshot_version(self, symbol: str, timeframe: str, snapshot_version: int) -> Optional[TSnapshot]:
        """
        Retrieves an upstream snapshot by its unique business version.
        """
        pass
        
    @abstractmethod
    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[TSnapshot]:
        """
        Retrieves the latest upstream snapshot for a given symbol and timeframe.
        """
        pass
