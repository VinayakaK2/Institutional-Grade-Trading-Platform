from abc import ABC, abstractmethod
from typing import Optional
from backend.trade_validation_engine.models.models import TradeValidationSnapshot

class ITradeValidationRepository(ABC):
    """
    Contract for the Trade Validation Repository.
    Responsible for async persistence of immutable snapshots.
    No business queries.
    """
    
    @abstractmethod
    async def save(self, snapshot: TradeValidationSnapshot) -> None:
        """
        Persists a newly created Trade Validation Snapshot.
        Must be an insert-only operation.
        """
        pass
        
    @abstractmethod
    async def get_by_id(self, snapshot_id: str) -> Optional[TradeValidationSnapshot]:
        """
        Retrieves a snapshot by its deterministic ID.
        """
        pass
