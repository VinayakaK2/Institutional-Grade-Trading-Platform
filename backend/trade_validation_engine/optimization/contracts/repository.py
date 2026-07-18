import abc
from typing import Optional, List
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot

class IOptimizationRepository(abc.ABC):
    """
    Contract for immutable OptimizationSnapshot persistence.
    """
    @abc.abstractmethod
    async def save(self, snapshot: OptimizationSnapshot) -> None:
        """Saves a single snapshot. INSERT-only."""
        pass

    @abc.abstractmethod
    async def save_many(self, snapshots: List[OptimizationSnapshot]) -> None:
        """Saves a batch of snapshots. INSERT-only."""
        pass

    @abc.abstractmethod
    async def load(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        """Loads an optimization snapshot by its ID."""
        pass

    @abc.abstractmethod
    async def exists(self, optimization_id: str) -> bool:
        """Checks if a snapshot exists."""
        pass

    @abc.abstractmethod
    async def load_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        """Loads a snapshot using its business fingerprint."""
        pass
