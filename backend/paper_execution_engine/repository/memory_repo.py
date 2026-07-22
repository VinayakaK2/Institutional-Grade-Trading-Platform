from typing import Dict
from backend.paper_execution_engine.contracts.repository import IPaperExecutionRepository
from backend.paper_execution_engine.models.snapshot import PaperExecutionSnapshot

class MemoryPaperExecutionRepository(IPaperExecutionRepository):
    """
    In-memory implementation of the paper execution repository.
    Strictly insert-only.
    """
    def __init__(self):
        self._snapshots: Dict[str, PaperExecutionSnapshot] = {}
        self._latest_id: str = None
        self._version_map: Dict[str, str] = {}
        
    async def save(self, snapshot: PaperExecutionSnapshot) -> None:
        if snapshot.snapshot_id in self._snapshots:
            raise ValueError(f"Duplicate snapshot ID: {snapshot.snapshot_id}")
            
        self._snapshots[snapshot.snapshot_id] = snapshot
        self._version_map[snapshot.pipeline_version] = snapshot.snapshot_id
        self._latest_id = snapshot.snapshot_id

    async def load(self, snapshot_id: str) -> PaperExecutionSnapshot:
        if snapshot_id not in self._snapshots:
            raise ValueError(f"Snapshot missing: {snapshot_id}")
        return self._snapshots[snapshot_id]

    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._snapshots

    async def load_latest(self) -> PaperExecutionSnapshot:
        if not self._latest_id:
            raise ValueError("No snapshots found")
        return self._snapshots[self._latest_id]
        
    async def load_by_snapshot_version(self, snapshot_version: str) -> PaperExecutionSnapshot:
        # For memory repo, iterating to find version. Alternatively we could map it.
        for snap in self._snapshots.values():
            if snap.snapshot_version == snapshot_version:
                return snap
        raise ValueError(f"Snapshot version missing: {snapshot_version}")
