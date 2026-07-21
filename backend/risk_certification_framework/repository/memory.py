from typing import Dict
import copy
import asyncio
from backend.risk_certification_framework.contracts.repository import IRiskCertificationRepository
from backend.risk_certification_framework.models.snapshot import RiskCertificationSnapshot

class MemoryCertificationRepository(IRiskCertificationRepository):
    def __init__(self):
        self._store: Dict[str, RiskCertificationSnapshot] = {}
        self._lock = asyncio.Lock()
        
    async def insert(self, snapshot: RiskCertificationSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_id in self._store:
                raise ValueError(f"Snapshot {snapshot.snapshot_id} already exists. Updates are strictly forbidden.")
            self._store[snapshot.snapshot_id] = copy.deepcopy(snapshot)
            
    async def get(self, snapshot_id: str) -> RiskCertificationSnapshot:
        async with self._lock:
            if snapshot_id not in self._store:
                raise KeyError(f"Snapshot {snapshot_id} not found.")
            return copy.deepcopy(self._store[snapshot_id])
