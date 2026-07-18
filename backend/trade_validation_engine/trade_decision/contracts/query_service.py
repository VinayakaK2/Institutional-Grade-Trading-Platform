import abc
from typing import Optional, List
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot

class ITradeDecisionQueryService(abc.ABC):
    """
    Read-only queries for TradeDecisionSnapshot, intended for analytics and presentation.
    """
    @abc.abstractmethod
    async def get_by_decision_id(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        pass

    @abc.abstractmethod
    async def get_latest_by_symbol(self, symbol: str) -> Optional[TradeDecisionSnapshot]:
        pass

    @abc.abstractmethod
    async def query_by_dataset_version(self, dataset_version: int, limit: int = 100, offset: int = 0) -> List[TradeDecisionSnapshot]:
        pass
