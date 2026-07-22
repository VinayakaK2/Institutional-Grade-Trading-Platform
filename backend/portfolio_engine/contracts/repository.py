from abc import ABC, abstractmethod
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot

class IPortfolioRepository(ABC):
    """
    INSERT-Only Repository for PortfolioSnapshots.
    Must guarantee Atomic Save OR No Save.
    """
    
    @abstractmethod
    async def save(self, snapshot: PortfolioSnapshot) -> None:
        """
        Inserts a new immutable portfolio snapshot.
        Must be atomic.
        """
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> PortfolioSnapshot:
        """
        Loads a snapshot by its deterministic ID.
        Raises KeyError if not found.
        """
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        """
        Checks if a snapshot exists.
        """
        pass
