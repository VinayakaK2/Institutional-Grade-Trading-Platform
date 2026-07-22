from abc import ABC, abstractmethod
from typing import Optional
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot

class IPortfolioCorrelationRepository(ABC):
    """
    INSERT-Only Repository for PortfolioCorrelationSnapshot.
    """
    @abstractmethod
    async def save(self, snapshot: PortfolioCorrelationSnapshot) -> None:
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> PortfolioCorrelationSnapshot:
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abstractmethod
    async def latest(self) -> Optional[PortfolioCorrelationSnapshot]:
        pass
