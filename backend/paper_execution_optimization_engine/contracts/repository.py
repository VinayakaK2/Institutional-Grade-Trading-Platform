from abc import ABC, abstractmethod
from typing import Optional, List
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot


class IPaperExecutionOptimizationRepository(ABC):
    """
    Append-only repository interface for optimization snapshots.
    """

    @abstractmethod
    async def save(self, snapshot: PaperExecutionOptimizationSnapshot) -> None:
        """
        Persists a snapshot. Must enforce unique constraints based on optimization_fingerprint
        and throw an IntegrityError (or domain equivalent) on duplicates.
        """
        pass

    @abstractmethod
    async def save_many(self, snapshots: List[PaperExecutionOptimizationSnapshot]) -> None:
        """
        Persists multiple snapshots efficiently in a single transaction.
        """
        pass

    @abstractmethod
    async def load(self, optimization_fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        """
        Loads a snapshot by its optimization fingerprint.
        Raises DomainException if not found.
        """
        pass

    @abstractmethod
    async def load_latest(self) -> Optional[PaperExecutionOptimizationSnapshot]:
        """
        Loads the most recently saved snapshot, if any.
        """
        pass
