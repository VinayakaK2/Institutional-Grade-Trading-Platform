from abc import ABC, abstractmethod
from typing import Optional
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot

class IPaperFillRepository(ABC):
    """
    Strict INSERT-only repository contract for PaperFillSnapshot persistence.
    UPDATE and DELETE are explicitly prohibited by this contract.
    """
    @abstractmethod
    def save(self, snapshot: PaperFillSnapshot) -> None:
        pass

    @abstractmethod
    def load(self, snapshot_id: str) -> Optional[PaperFillSnapshot]:
        pass

    @abstractmethod
    def exists(self, snapshot_id: str) -> bool:
        pass

    @abstractmethod
    def load_latest(self) -> Optional[PaperFillSnapshot]:
        pass
