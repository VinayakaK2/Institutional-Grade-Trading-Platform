from abc import ABC, abstractmethod
from typing import List, Optional
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot

class IPortfolioQueryService(ABC):
    """
    Projection-oriented read model interface.
    No business logic, only data retrieval.
    """
    
    @abstractmethod
    async def load_latest_snapshot(self, symbol: str, timeframe: str) -> Optional[PortfolioSnapshot]:
        pass
        
    @abstractmethod
    async def load_snapshot_lineage(self, parent_risk_snapshot_version: str) -> List[PortfolioSnapshot]:
        pass
