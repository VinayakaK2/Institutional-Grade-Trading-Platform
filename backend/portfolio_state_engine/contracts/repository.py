from abc import ABC, abstractmethod
from typing import Optional
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot

class IPortfolioStateRepository(ABC):
    """
    INSERT-Only Repository for PortfolioStateSnapshot.
    Must guarantee Atomic Save OR No Save.
    """
    
    @abstractmethod
    async def save(self, snapshot: PortfolioStateSnapshot) -> None:
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> PortfolioStateSnapshot:
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abstractmethod
    async def latest(self) -> Optional[PortfolioStateSnapshot]:
        pass
