from typing import Optional, List
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot
from backend.trade_validation_engine.trade_decision.contracts.query_service import ITradeDecisionQueryService
from backend.trade_validation_engine.trade_decision.repository.memory import InMemoryTradeDecisionRepository

class InMemoryTradeDecisionQueryService(ITradeDecisionQueryService):
    """
    In-memory query service built on top of the in-memory repository for testing.
    """
    def __init__(self, repository: InMemoryTradeDecisionRepository) -> None:
        self._repository = repository

    async def get_by_decision_id(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        return await self._repository.load(decision_id)

    async def get_latest_by_symbol(self, symbol: str) -> Optional[TradeDecisionSnapshot]:
        results = await self._repository.query_by_symbol(symbol)
        if not results:
            return None
        results.sort(key=lambda d: d.created_timestamp, reverse=True)
        return results[0]

    async def query_by_dataset_version(self, dataset_version: int, limit: int = 100, offset: int = 0) -> List[TradeDecisionSnapshot]:
        results = await self._repository.query_by_dataset_version(dataset_version)
        # Sort for consistent pagination (by created_timestamp descending)
        results.sort(key=lambda d: d.created_timestamp, reverse=True)
        return results[offset:offset+limit]
