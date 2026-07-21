import abc
from typing import Optional, List
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot

class IPositionSizingQueryService(abc.ABC):
    """
    Read-only Query Service Contract for Position Sizing Snapshots.
    """
    @abc.abstractmethod
    async def load(self, snapshot_id: str) -> Optional[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[PositionSizingSnapshot]:
        pass
        
    @abc.abstractmethod
    async def query_by_dataset_version(self, version: str) -> List[PositionSizingSnapshot]:
        pass
