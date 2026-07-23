from typing import Dict, List, Optional
from backend.paper_execution_result_engine.contracts.repository import PaperExecutionResultRepository
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultPersistenceError

class MemoryPaperExecutionResultRepository(PaperExecutionResultRepository):
    """
    In-memory immutable repository for execution result snapshots.
    Useful for testing and local deterministic replays.
    """
    def __init__(self) -> None:
        self._store: Dict[str, PaperExecutionSnapshot] = {}
        self._history: List[str] = []
        
    def save(self, snapshot: PaperExecutionSnapshot) -> None:
        if snapshot.snapshot_version in self._store:
            raise PaperExecutionResultPersistenceError(f"Snapshot version {snapshot.snapshot_version} already exists. Repositories are append-only.")
        self._store[snapshot.snapshot_version] = snapshot
        self._history.append(snapshot.snapshot_version)
        
    def exists(self, snapshot_version: str) -> bool:
        return snapshot_version in self._store
        
    def load(self, snapshot_version: str) -> PaperExecutionSnapshot:
        if snapshot_version not in self._store:
            raise PaperExecutionResultPersistenceError(f"Snapshot version {snapshot_version} not found.")
        return self._store[snapshot_version]
        
    def load_latest(self) -> Optional[PaperExecutionSnapshot]:
        if not self._history:
            return None
        return self._store[self._history[-1]]
        
    def list_all(self) -> List[PaperExecutionSnapshot]:
        return [self._store[version] for version in self._history]
