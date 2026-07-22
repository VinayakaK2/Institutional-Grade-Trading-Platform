from abc import ABC, abstractmethod
from typing import Optional
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot

class IPortfolioExposureRepository(ABC):
    """
    INSERT-Only Repository for PortfolioExposureSnapshot.
    """
    @abstractmethod
    async def save(self, snapshot: PortfolioExposureSnapshot) -> None:
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> PortfolioExposureSnapshot:
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abstractmethod
    async def latest(self) -> Optional[PortfolioExposureSnapshot]:
        pass
