"""
Candle Repository Contracts
Defines the generic storage abstractions for all dataset types.
"""
from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Any, Optional

from backend.candle_storage.models.dataset import CandleQueryFilters

class CandleRepositoryContract(ABC):
    """
    Contract for persisting and querying candle data generically.
    This repository relies on specific DatasetType to route queries/saves internally, 
    but provides a unified interface.
    """
    
    @abstractmethod
    async def save_batch(self, dataset_type: str, dataset_version: Optional[str], candles: List[Any]) -> None:
        """
        Saves a batch of candles in an idempotent, transaction-safe manner.
        :param dataset_type: String representation of DatasetType.
        :param dataset_version: Version string (only for adjusted), else None.
        :param candles: List of domain models (RawCandle or Candle).
        """
        pass
        
    @abstractmethod
    def get_stream(self, filters: CandleQueryFilters) -> AsyncGenerator[Any, None]:
        """
        Stream candles sequentially using explicit filters.
        """
        pass

    @abstractmethod
    async def delete_dataset(self, dataset_type: str, symbol_id: str, timeframe: str, dataset_version: Optional[str] = None) -> None:
        """
        Hard-deletes a specific symbol/timeframe dataset for teardown or version invalidation.
        """
        pass
