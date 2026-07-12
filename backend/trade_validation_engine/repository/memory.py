from typing import Dict, Optional
from backend.trade_validation_engine.contracts.repository import ITradeValidationRepository
from backend.trade_validation_engine.models.models import TradeValidationSnapshot
from backend.trade_validation_engine.exceptions.exceptions import RepositoryError

class InMemoryTradeValidationRepository(ITradeValidationRepository):
    """
    In-memory implementation of the Trade Validation Repository for testing.
    """
    
    def __init__(self):
        self._storage: Dict[str, TradeValidationSnapshot] = {}
        
    async def save(self, snapshot: TradeValidationSnapshot) -> None:
        try:
            # Enforce insert-only
            if snapshot.snapshot_id in self._storage:
                raise ValueError(f"Snapshot {snapshot.snapshot_id} already exists.")
            self._storage[snapshot.snapshot_id] = snapshot
        except Exception as e:
            raise RepositoryError(f"Failed to save snapshot: {str(e)}")
            
    async def get_by_id(self, snapshot_id: str) -> Optional[TradeValidationSnapshot]:
        return self._storage.get(snapshot_id)
