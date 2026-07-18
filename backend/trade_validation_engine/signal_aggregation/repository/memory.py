from typing import Optional, Dict
from backend.trade_validation_engine.signal_aggregation.contracts.repository import ISignalAggregationRepository
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import RepositoryError

class InMemorySignalAggregationRepository(ISignalAggregationRepository):
    """
    In-memory implementation of the Signal Aggregation Repository.
    Used for testing and deterministic execution.
    """
    def __init__(self):
        self._storage: Dict[str, SignalAggregationSnapshot] = {}

    async def save(self, snapshot: SignalAggregationSnapshot) -> None:
        if snapshot.aggregation_id in self._storage:
            raise RepositoryError(f"Snapshot with ID {snapshot.aggregation_id} already exists (Immutability violation).")
        self._storage[snapshot.aggregation_id] = snapshot

    async def get_by_id(self, aggregation_id: str) -> Optional[SignalAggregationSnapshot]:
        return self._storage.get(aggregation_id)
        
    async def exists(self, aggregation_id: str) -> bool:
        return aggregation_id in self._storage
