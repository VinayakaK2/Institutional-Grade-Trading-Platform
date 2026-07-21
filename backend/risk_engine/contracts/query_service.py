import abc
from typing import Optional, List
from backend.risk_engine.models.snapshot import RiskSnapshot

class IRiskSnapshotQueryService(abc.ABC):
    """
    Read-only Query Service Contract for Risk Snapshots.
    """
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[RiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[RiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_parent_trade_decision_snapshot(self, parent_id: str) -> List[RiskSnapshot]:
        pass
        
    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[RiskSnapshot]:
        pass
