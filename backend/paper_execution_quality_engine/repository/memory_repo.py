import copy
import threading
from typing import Optional, Dict, List
from backend.paper_execution_quality_engine.contracts.repository import IPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityPersistenceError

class MemoryPaperExecutionQualityRepository(IPaperExecutionQualityRepository):
    """
    In-memory INSERT-only repository for paper execution quality snapshots.
    """
    def __init__(self):
        self._store: Dict[str, PaperExecutionQualitySnapshot] = {}
        self._latest_version: Optional[str] = None
        self._lock = threading.Lock()

    def save(self, snapshot: PaperExecutionQualitySnapshot) -> None:
        with self._lock:
            if snapshot.snapshot_version in self._store:
                raise PaperExecutionQualityPersistenceError(
                    f"Snapshot with version {snapshot.snapshot_version} already exists. Updates are not allowed."
                )
            
            self._store[snapshot.snapshot_version] = copy.deepcopy(snapshot)
            self._latest_version = snapshot.snapshot_version

    def load(self, snapshot_id: str) -> Optional[PaperExecutionQualitySnapshot]:
        with self._lock:
            return self._store.get(snapshot_id)

    def exists(self, snapshot_id: str) -> bool:
        with self._lock:
            return snapshot_id in self._store

    def load_latest(self) -> Optional[PaperExecutionQualitySnapshot]:
        with self._lock:
            if self._latest_version:
                return self._store.get(self._latest_version)
            return None
            
    def query_by_parent_fill_snapshot(self, version: str) -> List[PaperExecutionQualitySnapshot]:
        with self._lock:
            return [s for s in self._store.values() if s.parent_fill_snapshot_version == version]
