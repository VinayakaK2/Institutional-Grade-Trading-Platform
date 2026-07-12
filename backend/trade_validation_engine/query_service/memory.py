from typing import List, Optional
from backend.trade_validation_engine.contracts.query_service import ITradeValidationQueryService
from backend.trade_validation_engine.models.models import TradeValidationSnapshot

class InMemoryTradeValidationQueryService(ITradeValidationQueryService):
    """
    In-memory implementation of the Query Service for testing.
    Shares the same storage reference as the InMemoryRepository.
    """
    
    def __init__(self, storage: dict):
        self._storage = storage
        
    async def get_by_id(self, snapshot_id: str) -> Optional[TradeValidationSnapshot]:
        return self._storage.get(snapshot_id)
        
    async def get_latest_by_symbol(self, symbol: str, timeframe: str) -> Optional[TradeValidationSnapshot]:
        # Sort by created timestamp descending
        matches = [s for s in self._storage.values() if s.symbol == symbol and s.timeframe == timeframe]
        if not matches:
            return None
        matches.sort(key=lambda s: s.metadata.created_timestamp, reverse=True)
        return matches[0]
        
    async def get_by_snapshot_version(self, symbol: str, timeframe: str, version_key: str, version_val: int) -> List[TradeValidationSnapshot]:
        results = []
        for s in self._storage.values():
            if s.symbol == symbol and s.timeframe == timeframe:
                # Dynamically check context field based on version_key
                val = getattr(s.context, version_key, None)
                if val == version_val:
                    results.append(s)
        return results
        
    async def list_paginated(self, symbol: str, limit: int = 50, offset: int = 0) -> List[TradeValidationSnapshot]:
        matches = [s for s in self._storage.values() if s.symbol == symbol]
        matches.sort(key=lambda s: s.metadata.created_timestamp, reverse=True)
        return matches[offset:offset+limit]
