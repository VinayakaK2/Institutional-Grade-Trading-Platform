from typing import Optional, Dict
from backend.paper_order_engine.contracts.repository import IPaperOrderRepository
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot
from backend.paper_order_engine.exceptions.exceptions import PaperOrderPersistenceError

class MemoryPaperOrderRepository(IPaperOrderRepository):
    """
    In-memory INSERT-only repository for paper order snapshots.
    """
    def __init__(self):
        self._store: Dict[str, PaperOrderSnapshot] = {}
        self._latest_snapshot_id: Optional[str] = None
        
    def save(self, snapshot: PaperOrderSnapshot) -> None:
        if self.exists(snapshot.snapshot_id):
            raise PaperOrderPersistenceError(f"Duplicate snapshot ID: {snapshot.snapshot_id}")
        self._store[snapshot.snapshot_id] = snapshot
        self._latest_snapshot_id = snapshot.snapshot_id

    def load(self, snapshot_id: str) -> Optional[PaperOrderSnapshot]:
        return self._store.get(snapshot_id)

    def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._store

    def load_latest(self) -> Optional[PaperOrderSnapshot]:
        if self._latest_snapshot_id:
            return self._store.get(self._latest_snapshot_id)
        return None

    def load_by_snapshot_version(self, version: str) -> Optional[PaperOrderSnapshot]:
        for snapshot in self._store.values():
            if snapshot.snapshot_version == version:
                return snapshot
        return None
