from typing import Optional, List, Dict
from backend.trade_validation_engine.signal_aggregation.contracts.query_service import ISignalAggregationQueryService
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot

class InMemorySignalAggregationQueryService(ISignalAggregationQueryService):
    """
    In-memory read-only query service for testing.
    """
    def __init__(self, storage: Dict[str, SignalAggregationSnapshot]):
        self._storage = storage

    async def get_by_aggregation_id(self, aggregation_id: str) -> Optional[SignalAggregationSnapshot]:
        return self._storage.get(aggregation_id)

    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[SignalAggregationSnapshot]:
        matches = [s for s in self._storage.values() if s.symbol == symbol and s.timeframe == timeframe]
        if not matches:
            return None
        matches.sort(key=lambda s: s.metadata.created_timestamp, reverse=True)
        return matches[0]

    async def list_paginated(self, symbol: str, limit: int = 100, offset: int = 0) -> List[SignalAggregationSnapshot]:
        matches = [s for s in self._storage.values() if s.symbol == symbol]
        matches.sort(key=lambda s: s.metadata.created_timestamp, reverse=True)
        return matches[offset:offset+limit]

    async def get_by_dataset_version(self, dataset_version: int) -> List[SignalAggregationSnapshot]:
        matches = [s for s in self._storage.values() if s.aggregated_evidence and s.aggregated_evidence.dataset_version == dataset_version]
        matches.sort(key=lambda s: s.metadata.created_timestamp, reverse=True)
        return matches
