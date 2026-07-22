from typing import Dict
from backend.portfolio_certification_framework.contracts.repository import IPortfolioCertificationRepository
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot

class MemoryPortfolioCertificationRepository(IPortfolioCertificationRepository):
    def __init__(self):
        self._snapshots: Dict[str, PortfolioCertificationSnapshot] = {}
        self._latest_id: str = None
        
    async def save(self, snapshot: PortfolioCertificationSnapshot) -> None:
        if snapshot.snapshot_id in self._snapshots:
            raise ValueError(f"Duplicate snapshot ID: {snapshot.snapshot_id}")
            
        self._snapshots[snapshot.snapshot_id] = snapshot
        self._latest_id = snapshot.snapshot_id

    async def load(self, snapshot_id: str) -> PortfolioCertificationSnapshot:
        if snapshot_id not in self._snapshots:
            raise ValueError(f"Snapshot missing: {snapshot_id}")
        return self._snapshots[snapshot_id]

    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self._snapshots

    async def load_latest(self) -> PortfolioCertificationSnapshot:
        if not self._latest_id:
            raise ValueError("No snapshots available")
        return self._snapshots[self._latest_id]
