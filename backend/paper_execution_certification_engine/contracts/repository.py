from abc import ABC, abstractmethod
from typing import Optional
from backend.paper_execution_certification_engine.models.snapshot import PaperExecutionCertificationSnapshot

class IPaperExecutionCertificationRepository(ABC):
    """
    Append-only repository for paper execution certifications.
    Must maintain immutability and determinism.
    """
    
    @abstractmethod
    async def save(self, snapshot: PaperExecutionCertificationSnapshot) -> None:
        """Saves a certification snapshot. Raises CertificationRepositoryIntegrityError on duplication attempt."""
        pass
        
    @abstractmethod
    async def load(self, snapshot_version: str) -> PaperExecutionCertificationSnapshot:
        """Loads a certification snapshot. Raises CertificationRepositoryNotFoundError if not found."""
        pass
        
    @abstractmethod
    async def exists(self, snapshot_version: str) -> bool:
        """Checks if a snapshot exists."""
        pass
        
    @abstractmethod
    async def load_latest(self, parent_execution_snapshot_version: str) -> Optional[PaperExecutionCertificationSnapshot]:
        """Loads the most recent certification for a given execution snapshot."""
        pass
