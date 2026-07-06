from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorQueryFilters

class IndicatorRepositoryContract(ABC):
    """
    Contract for persisting and retrieving IndicatorResults.
    Must be infrastructure only.
    """
    
    @abstractmethod
    async def save_batch(self, indicators: List[IndicatorResult]) -> None:
        """
        Saves a batch of indicators idempotently.
        """
        pass
        
    @abstractmethod
    def get_stream(self, filters: IndicatorQueryFilters) -> AsyncGenerator[IndicatorResult, None]:
        """
        Retrieves a stream of IndicatorResult matching the filters.
        """
        pass

    @abstractmethod
    async def get_latest_timestamp(self, filters: IndicatorQueryFilters) -> str:
        """
        Retrieves the latest timestamp for a specific indicator series.
        Used for incremental updates.
        Returns empty string if none exist.
        """
        pass
