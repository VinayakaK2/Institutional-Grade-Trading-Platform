from abc import ABC, abstractmethod
from backend.universe_engine.models.universe import UniverseResult

class IUniverseEngine(ABC):
    @abstractmethod
    async def generate_universe(self, run_id: str) -> UniverseResult:
        pass
