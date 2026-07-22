import abc
from typing import Optional
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot

class IPortfolioDecisionRepository(abc.ABC):
    """
    Strict INSERT-only repository contract for PortfolioDecisionSnapshot persistence.
    """
    @abc.abstractmethod
    def save(self, snapshot: PortfolioDecisionSnapshot) -> None:
        pass

    @abc.abstractmethod
    def load(self, snapshot_id: str) -> Optional[PortfolioDecisionSnapshot]:
        pass

    @abc.abstractmethod
    def exists(self, snapshot_id: str) -> bool:
        pass

    @abc.abstractmethod
    def load_latest(self) -> Optional[PortfolioDecisionSnapshot]:
        pass

    @abc.abstractmethod
    def load_by_business_fingerprint(self, fingerprint: str) -> Optional[PortfolioDecisionSnapshot]:
        pass
