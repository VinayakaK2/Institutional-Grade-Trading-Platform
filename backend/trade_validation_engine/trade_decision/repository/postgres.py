from typing import Optional, List
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot
from backend.trade_validation_engine.trade_decision.contracts.repository import ITradeDecisionRepository

class PostgresTradeDecisionRepository(ITradeDecisionRepository):
    """
    PostgreSQL stub for ITradeDecisionRepository.
    Raises NotImplementedError as per Phase 10.4 requirements.
    """
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    async def save(self, decision: TradeDecisionSnapshot) -> None:
        raise NotImplementedError("PostgresTradeDecisionRepository.save is not implemented")

    async def load(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.load is not implemented")

    async def exists(self, decision_id: str) -> bool:
        raise NotImplementedError("PostgresTradeDecisionRepository.exists is not implemented")

    async def query_by_symbol(self, symbol: str) -> List[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.query_by_symbol is not implemented")

    async def query_by_timeframe(self, timeframe: str) -> List[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.query_by_timeframe is not implemented")

    async def query_by_validation_report(self, validation_report_version: str) -> List[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.query_by_validation_report is not implemented")

    async def query_by_dataset_version(self, dataset_version: int) -> List[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.query_by_dataset_version is not implemented")

    async def load_latest(self, symbol: str, timeframe: str) -> Optional[TradeDecisionSnapshot]:
        raise NotImplementedError("PostgresTradeDecisionRepository.load_latest is not implemented")
