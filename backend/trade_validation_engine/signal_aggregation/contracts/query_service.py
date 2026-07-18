from abc import ABC, abstractmethod
from typing import Optional, List
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot

class ISignalAggregationQueryService(ABC):
    """
    Contract for read-only queries against Signal Aggregation Snapshots.
    """
    @abstractmethod
    async def get_by_aggregation_id(self, aggregation_id: str) -> Optional[SignalAggregationSnapshot]:
        """Retrieves a snapshot by its deterministic ID."""
        pass

    @abstractmethod
    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[SignalAggregationSnapshot]:
        """Retrieves the most recent snapshot for a symbol and timeframe."""
        pass

    @abstractmethod
    async def list_paginated(self, symbol: str, limit: int = 100, offset: int = 0) -> List[SignalAggregationSnapshot]:
        """Retrieves paginated snapshots for a symbol."""
        pass
        
    @abstractmethod
    async def get_by_dataset_version(self, dataset_version: int) -> List[SignalAggregationSnapshot]:
        """Retrieves snapshots matching a specific dataset version."""
        pass
