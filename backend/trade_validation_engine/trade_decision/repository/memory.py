from typing import Optional, List, Dict
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot
from backend.trade_validation_engine.trade_decision.contracts.repository import ITradeDecisionRepository

class InMemoryTradeDecisionRepository(ITradeDecisionRepository):
    """
    In-memory implementation for testing and development.
    """
    def __init__(self) -> None:
        self._storage: Dict[str, TradeDecisionSnapshot] = {}

    async def save(self, decision: TradeDecisionSnapshot) -> None:
        # INSERT-only emulation
        if decision.decision_id not in self._storage:
            self._storage[decision.decision_id] = decision

    async def load(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        return self._storage.get(decision_id)

    async def exists(self, decision_id: str) -> bool:
        return decision_id in self._storage

    async def query_by_symbol(self, symbol: str) -> List[TradeDecisionSnapshot]:
        return [d for d in self._storage.values() if d.symbol == symbol]

    async def query_by_timeframe(self, timeframe: str) -> List[TradeDecisionSnapshot]:
        return [d for d in self._storage.values() if d.timeframe == timeframe]

    async def query_by_validation_report(self, validation_report_version: str) -> List[TradeDecisionSnapshot]:
        return [d for d in self._storage.values() if d.validation_report_version == validation_report_version]

    async def query_by_dataset_version(self, dataset_version: int) -> List[TradeDecisionSnapshot]:
        return [d for d in self._storage.values() if d.dataset_version == dataset_version]

    async def load_latest(self, symbol: str, timeframe: str) -> Optional[TradeDecisionSnapshot]:
        results = [d for d in self._storage.values() if d.symbol == symbol and d.timeframe == timeframe]
        if not results:
            return None
        # Sort by creation time descending and return the first
        results.sort(key=lambda d: d.created_timestamp, reverse=True)
        return results[0]
