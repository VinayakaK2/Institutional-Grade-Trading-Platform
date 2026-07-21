from abc import ABC, abstractmethod
from typing import Optional, List
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.risk_decision_engine.models.evidence import DecisionType

class IRiskDecisionSnapshotRepository(ABC):
    @abstractmethod
    async def save(self, snapshot: RiskDecisionSnapshot) -> None:
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> Optional[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_decision(self, decision: DecisionType) -> List[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_parent_portfolio_snapshot(self, portfolio_snapshot_id: str) -> List[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[RiskDecisionSnapshot]:
        pass
