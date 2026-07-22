from typing import Optional, Dict
from backend.portfolio_decision_engine.contracts.repository import IPortfolioDecisionRepository
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot

class MemoryPortfolioDecisionRepository(IPortfolioDecisionRepository):
    """
    In-memory INSERT-only repository for PortfolioDecisionSnapshots.
    """
    def __init__(self):
        self._store: Dict[str, PortfolioDecisionSnapshot] = {}
        self._latest_id: Optional[str] = None

    def save(self, snapshot: PortfolioDecisionSnapshot) -> None:
        if snapshot.snapshot_id in self._store:
            raise ValueError(f"Snapshot {snapshot.snapshot_id} already exists. Repository is INSERT-only.")
        self._store[snapshot.snapshot_id] = snapshot
        self._latest_id = snapshot.snapshot_id

    def load(self, snapshot_id: str) -> Optional[PortfolioDecisionSnapshot]:
        return self._store.get(snapshot_id)

    def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._store

    def load_latest(self) -> Optional[PortfolioDecisionSnapshot]:
        if self._latest_id:
            return self._store.get(self._latest_id)
        return None

    def load_by_business_fingerprint(self, fingerprint: str) -> Optional[PortfolioDecisionSnapshot]:
        for snapshot in self._store.values():
            if snapshot.business_fingerprint == fingerprint:
                return snapshot
        return None
