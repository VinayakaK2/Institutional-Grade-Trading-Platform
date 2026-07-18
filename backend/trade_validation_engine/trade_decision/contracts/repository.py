import abc
from typing import Optional, List
from backend.trade_validation_engine.trade_decision.models.models import TradeDecisionSnapshot

class ITradeDecisionRepository(abc.ABC):
    """
    Contract for immutable TradeDecisionSnapshot persistence.
    """
    @abc.abstractmethod
    async def save(self, decision: TradeDecisionSnapshot) -> None:
        """Saves a decision snapshot. Should be INSERT-only."""
        pass

    @abc.abstractmethod
    async def load(self, decision_id: str) -> Optional[TradeDecisionSnapshot]:
        """Loads a decision snapshot by its ID."""
        pass

    @abc.abstractmethod
    async def exists(self, decision_id: str) -> bool:
        """Checks if a decision snapshot exists."""
        pass

    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[TradeDecisionSnapshot]:
        """Queries decisions by symbol."""
        pass

    @abc.abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[TradeDecisionSnapshot]:
        """Queries decisions by timeframe."""
        pass

    @abc.abstractmethod
    async def query_by_validation_report(self, validation_report_version: str) -> List[TradeDecisionSnapshot]:
        """Queries decisions derived from a specific validation report."""
        pass

    @abc.abstractmethod
    async def query_by_dataset_version(self, dataset_version: int) -> List[TradeDecisionSnapshot]:
        """Queries decisions by dataset version."""
        pass

    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[TradeDecisionSnapshot]:
        """Loads the most recent decision snapshot for a symbol and timeframe."""
        pass
