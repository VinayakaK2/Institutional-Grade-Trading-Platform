from abc import ABC, abstractmethod
from typing import Optional
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot

class IPortfolioOptimizationRepository(ABC):
    """
    Contract for persistence of portfolio optimization snapshots.
    """
    
    @abstractmethod
    async def save(self, snapshot: PortfolioOptimizationSnapshot) -> None:
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> Optional[PortfolioOptimizationSnapshot]:
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[PortfolioOptimizationSnapshot]:
        pass
