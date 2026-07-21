import abc
from typing import Optional, List
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot

class IPositionRiskSnapshotRepository(abc.ABC):
    """
    Contract for Position Risk Snapshot persistence.
    """
    @abc.abstractmethod
    async def save(self, snapshot: RiskEvaluationSnapshot) -> None:
        pass
        
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_trade_decision_snapshot(self, parent_id: str) -> List[RiskEvaluationSnapshot]:
        pass

    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[RiskEvaluationSnapshot]:
        pass
