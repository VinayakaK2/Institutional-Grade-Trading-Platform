"""
Candle Storage & Query Engine Contracts
"""
from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Any

from backend.candle_storage.models.dataset import CandleQueryFilters

class CandleStorageEngineContract(ABC):
    """
    Contract for orchestrating writes, validation, and idempotent saves.
    """
    
    @abstractmethod
    async def save_raw_candles(self, candles: List[Any]) -> None:
        pass
        
    @abstractmethod
    async def save_canonical_candles(self, candles: List[Any]) -> None:
        pass
        
    @abstractmethod
    async def save_adjusted_candles(self, dataset_version: str, candles: List[Any]) -> None:
        pass


class CandleQueryEngineContract(ABC):
    """
    Contract for orchestrating queries, ensuring explicit dataset selection.
    """
    
    @abstractmethod
    def query(self, filters: CandleQueryFilters) -> AsyncGenerator[Any, None]:
        """
        Executes a query based on the explicit filters.
        Ensures strict boundary checks.
        """
        pass
