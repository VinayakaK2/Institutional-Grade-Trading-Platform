from abc import ABC, abstractmethod
from typing import Optional
from backend.universe_engine.models.universe import UniverseSnapshot

class IUniverseRepository(ABC):
    @abstractmethod
    async def save_snapshot(self, snapshot: UniverseSnapshot) -> None:
        pass

    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[UniverseSnapshot]:
        pass

    @abstractmethod
    async def load_latest_snapshot(self) -> Optional[UniverseSnapshot]:
        pass
