import abc
from typing import List, Optional
from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot

class IPortfolioRiskQueryService(abc.ABC):
    """
    Read-only query service for PortfolioRiskSnapshots.
    """
    
    @abc.abstractmethod
    async def get_snapshot(self, snapshot_id: str) -> Optional[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def get_snapshots_for_symbol(self, symbol: str) -> List[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def get_latest_snapshot(self) -> Optional[PortfolioRiskSnapshot]:
        pass
