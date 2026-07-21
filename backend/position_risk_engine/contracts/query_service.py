import abc
from typing import Optional, List
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot

class IPositionRiskQueryService(abc.ABC):
    """
    Read-only Query Service Contract for Position Risk Snapshots.
    """
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[RiskEvaluationSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_dataset_version(self, version: int) -> List[RiskEvaluationSnapshot]:
        pass
