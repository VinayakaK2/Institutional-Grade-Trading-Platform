from abc import ABC, abstractmethod
from typing import List, Optional
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.models.models import LiquidityGrabSnapshot

class ILiquidityGrabRepository(ABC):
    """
    Repository contract for Liquidity Grab Snapshots.
    Must be implemented as an INSERT-only store.
    """
    
    @abstractmethod
    async def save(self, snapshot: LiquidityGrabSnapshot) -> None:
        """Saves a new snapshot."""
        pass
        
    @abstractmethod
    async def load(self, snapshot_id: str) -> Optional[LiquidityGrabSnapshot]:
        """Loads a snapshot by its deterministic ID."""
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        """Checks if a snapshot exists."""
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabSnapshot]:
        """Queries snapshots by symbol ID."""
        pass
        
    @abstractmethod
    async def query_by_timeframe(self, timeframe: Timeframe) -> List[LiquidityGrabSnapshot]:
        """Queries snapshots by Timeframe."""
        pass
        
    @abstractmethod
    async def query_by_parent_trend_snapshot(self, trend_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        """Queries snapshots derived from a specific trend snapshot."""
        pass
        
    @abstractmethod
    async def query_by_consolidation_snapshot(self, consolidation_snapshot_version: int) -> List[LiquidityGrabSnapshot]:
        """Queries snapshots derived from a specific consolidation snapshot."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[LiquidityGrabSnapshot]:
        """Loads the most recently created snapshot."""
        pass
