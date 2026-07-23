from typing import Optional, Dict
from backend.paper_fill_engine.contracts.repository import IPaperFillRepository
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot
from backend.paper_fill_engine.exceptions.exceptions import PaperFillPersistenceError

class MemoryPaperFillRepository(IPaperFillRepository):
    """
    In-memory INSERT-only repository for paper fill snapshots.
    Updates and deletes are explicitly prohibited.
    """
    def __init__(self):
        self._store: Dict[str, PaperFillSnapshot] = {}
        self._latest_snapshot_id: Optional[str] = None
        
    def save(self, snapshot: PaperFillSnapshot) -> None:
        if self.exists(snapshot.snapshot_id):
            raise PaperFillPersistenceError(f"Duplicate snapshot ID: {snapshot.snapshot_id}")
        self._store[snapshot.snapshot_id] = snapshot
        self._latest_snapshot_id = snapshot.snapshot_id

    def load(self, snapshot_id: str) -> Optional[PaperFillSnapshot]:
        return self._store.get(snapshot_id)

    def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._store

    def load_latest(self) -> Optional[PaperFillSnapshot]:
        if self._latest_snapshot_id:
            return self._store.get(self._latest_snapshot_id)
        return None
