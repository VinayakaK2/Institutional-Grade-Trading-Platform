from abc import ABC, abstractmethod
from typing import List, Optional
from backend.paper_execution_result_engine.models.snapshot import PaperExecutionSnapshot

class PaperExecutionResultRepository(ABC):
    """
    Append-only repository contract for PaperExecutionSnapshot.
    No update or delete operations are permitted.
    """
    @abstractmethod
    def save(self, snapshot: PaperExecutionSnapshot) -> None:
        pass
        
    @abstractmethod
    def load(self, snapshot_version: str) -> PaperExecutionSnapshot:
        pass
        
    @abstractmethod
    def exists(self, snapshot_version: str) -> bool:
        pass
        
    @abstractmethod
    def load_latest(self) -> Optional[PaperExecutionSnapshot]:
        pass
        
    @abstractmethod
    def list_all(self) -> List[PaperExecutionSnapshot]:
        pass
