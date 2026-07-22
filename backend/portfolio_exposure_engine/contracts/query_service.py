from abc import ABC, abstractmethod
from typing import List, Optional
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot

class IPortfolioExposureQueryService(ABC):
    """
    Projection-oriented read-only service for Portfolio Exposure.
    """
    
    @abstractmethod
    async def get_latest_exposure(self) -> Optional[PortfolioExposureSnapshot]:
        pass
        
    @abstractmethod
    async def get_history(self) -> List[PortfolioExposureSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[PortfolioExposureSnapshot]:
        pass
