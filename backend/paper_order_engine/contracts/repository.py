from abc import ABC, abstractmethod
from typing import Optional
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot

class IPaperOrderRepository(ABC):
    """
    Strict INSERT-only repository contract for PaperOrderSnapshot persistence.
    """
    @abstractmethod
    def save(self, snapshot: PaperOrderSnapshot) -> None:
        pass

    @abstractmethod
    def load(self, snapshot_id: str) -> Optional[PaperOrderSnapshot]:
        pass

    @abstractmethod
    def exists(self, snapshot_id: str) -> bool:
        pass

    @abstractmethod
    def load_latest(self) -> Optional[PaperOrderSnapshot]:
        pass

    @abstractmethod
    def load_by_snapshot_version(self, version: str) -> Optional[PaperOrderSnapshot]:
        pass
