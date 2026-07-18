from typing import Optional, List
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot
from backend.trade_validation_engine.trade_decision.contracts.query_service import ITradeDecisionQueryService

class PostgresTradeDecisionQueryService(ITradeDecisionQueryService):
    """
    PostgreSQL stub for ITradeDecisionQueryService.
    Raises NotImplementedError.
    """
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    async def get_by_decision_id(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionQueryService.get_by_decision_id is not implemented")

    async def get_latest_by_symbol(self, symbol: str) -> Optional[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionQueryService.get_latest_by_symbol is not implemented")

    async def query_by_dataset_version(self, dataset_version: int, limit: int = 100, offset: int = 0) -> List[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionQueryService.query_by_dataset_version is not implemented")
