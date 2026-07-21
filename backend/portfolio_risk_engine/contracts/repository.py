import abc
from typing import List, Optional
from backend.portfolio_risk_engine.models.snapshot import PortfolioRiskSnapshot

class IPortfolioRiskSnapshotRepository(abc.ABC):
    """
    INSERT-only repository contract for PortfolioRiskSnapshots.
    """
    
    @abc.abstractmethod
    async def save(self, snapshot: PortfolioRiskSnapshot) -> None:
        pass
        
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_timeframe(self, start_time: str, end_time: str) -> List[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_parent_risk_snapshot(self, risk_snapshot_id: str) -> List[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_parent_position_sizing_snapshot(self, sizing_snapshot_id: str) -> List[PortfolioRiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def load_latest(self) -> Optional[PortfolioRiskSnapshot]:
        pass
