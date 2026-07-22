from abc import ABC, abstractmethod
from backend.paper_execution_engine.models.snapshot import PaperExecutionSnapshot

class IPaperExecutionRepository(ABC):
    """
    Interface for paper execution repository operations.
    Keeps repository INSERT-only.
    """
    
    @abstractmethod
    async def save(self, snapshot: PaperExecutionSnapshot) -> None:
        pass

    @abstractmethod
    async def load(self, snapshot_id: str) -> PaperExecutionSnapshot:
        pass

    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass

    @abstractmethod
    async def load_latest(self) -> PaperExecutionSnapshot:
        pass
        
    @abstractmethod
    async def load_by_snapshot_version(self, snapshot_version: str) -> PaperExecutionSnapshot:
        pass
