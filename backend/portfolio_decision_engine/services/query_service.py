from typing import Optional
from backend.portfolio_decision_engine.contracts.repository import IPortfolioDecisionRepository
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot

class PortfolioDecisionQueryService:
    """
    Read-only service for interacting with the portfolio decision repository.
    """
    def __init__(self, repository: IPortfolioDecisionRepository):
        self._repository = repository

    def get_snapshot(self, snapshot_id: str) -> Optional[PortfolioDecisionSnapshot]:
        return self._repository.load(snapshot_id)

    def get_latest(self) -> Optional[PortfolioDecisionSnapshot]:
        return self._repository.load_latest()

    def get_by_business_fingerprint(self, fingerprint: str) -> Optional[PortfolioDecisionSnapshot]:
        return self._repository.load_by_business_fingerprint(fingerprint)
