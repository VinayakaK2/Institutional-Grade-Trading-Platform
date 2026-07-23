from abc import ABC, abstractmethod
from typing import Optional, List
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot

class IPaperExecutionQualityRepository(ABC):
    """
    Strict INSERT-only repository contract for PaperExecutionQualitySnapshot persistence.
    UPDATE and DELETE are explicitly prohibited by this contract.
    """
    @abstractmethod
    def save(self, snapshot: PaperExecutionQualitySnapshot) -> None:
        pass

    @abstractmethod
    def load(self, snapshot_id: str) -> Optional[PaperExecutionQualitySnapshot]:
        pass

    @abstractmethod
    def exists(self, snapshot_id: str) -> bool:
        pass

    @abstractmethod
    def load_latest(self) -> Optional[PaperExecutionQualitySnapshot]:
        pass
        
    @abstractmethod
    def query_by_parent_fill_snapshot(self, version: str) -> List[PaperExecutionQualitySnapshot]:
        pass
