from abc import ABC, abstractmethod
from typing import Optional
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot

class ISignalAggregationRepository(ABC):
    """
    Contract for persisting Signal Aggregation Snapshots.
    Supports INSERT-only operations for immutability.
    """
    @abstractmethod
    async def save(self, snapshot: SignalAggregationSnapshot) -> None:
        """Saves a new snapshot."""
        pass

    @abstractmethod
    async def get_by_id(self, aggregation_id: str) -> Optional[SignalAggregationSnapshot]:
        """Retrieves a snapshot by its deterministic ID."""
        pass
        
    @abstractmethod
    async def exists(self, aggregation_id: str) -> bool:
        """Checks if a snapshot exists."""
        pass
