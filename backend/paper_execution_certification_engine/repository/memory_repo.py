import asyncio
from typing import Dict, Optional, List
from backend.paper_execution_certification_engine.contracts.repository import IPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.models.snapshot import PaperExecutionCertificationSnapshot
from backend.paper_execution_certification_engine.exceptions.exceptions import (
    CertificationRepositoryIntegrityError,
    CertificationRepositoryNotFoundError
)

class MemoryPaperExecutionCertificationRepository(IPaperExecutionCertificationRepository):
    """
    In-memory append-only repository for certifications.
    Ensures immutability and duplicate safety.
    """
    
    def __init__(self):
        self._store: Dict[str, PaperExecutionCertificationSnapshot] = {}
        self._parent_index: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        
    async def save(self, snapshot: PaperExecutionCertificationSnapshot) -> None:
        async with self._lock:
            if snapshot.snapshot_version in self._store:
                raise CertificationRepositoryIntegrityError(f"Snapshot {snapshot.snapshot_version} already exists. Repository is append-only.")
            
            self._store[snapshot.snapshot_version] = snapshot
            
            # Index by parent execution snapshot for query capabilities
            if snapshot.parent_execution_snapshot_version not in self._parent_index:
                self._parent_index[snapshot.parent_execution_snapshot_version] = []
            self._parent_index[snapshot.parent_execution_snapshot_version].append(snapshot.snapshot_version)

    async def load(self, snapshot_version: str) -> PaperExecutionCertificationSnapshot:
        async with self._lock:
            if snapshot_version not in self._store:
                raise CertificationRepositoryNotFoundError(f"Certification {snapshot_version} not found.")
            return self._store[snapshot_version]
            
    async def exists(self, snapshot_version: str) -> bool:
        async with self._lock:
            return snapshot_version in self._store
            
    async def load_latest(self, parent_execution_snapshot_version: str) -> Optional[PaperExecutionCertificationSnapshot]:
        async with self._lock:
            if parent_execution_snapshot_version not in self._parent_index:
                return None
                
            versions = self._parent_index[parent_execution_snapshot_version]
            if not versions:
                return None
                
            # For simplicity in memory, we assume the last appended is the latest
            latest_version = versions[-1]
            return self._store[latest_version]
