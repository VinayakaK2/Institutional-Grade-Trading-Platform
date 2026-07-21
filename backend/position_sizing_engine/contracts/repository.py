import abc
from typing import Optional, List
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot

class IPositionSizingSnapshotRepository(abc.ABC):
    """
    Contract for Position Sizing Snapshot persistence.
    """
    @abc.abstractmethod
    async def save(self, snapshot: PositionSizingSnapshot) -> None:
        pass
        
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_parent_risk_snapshot(self, parent_id: str) -> List[PositionSizingSnapshot]:
        pass

    @abc.abstractmethod
    async def query_by_dataset_version(self, dataset_version: str) -> List[PositionSizingSnapshot]:
        pass

    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[PositionSizingSnapshot]:
        pass
