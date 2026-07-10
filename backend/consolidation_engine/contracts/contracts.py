from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from backend.market_data.models.candle import Candle
from backend.consolidation_engine.models.models import ConsolidationCandidate, ConsolidationSnapshot

class IBoundaryDetectionStrategy(ABC):
    """Business strategy for determining the upper and lower boundaries of a consolidation range."""
    
    @abstractmethod
    def detect_boundaries(self, candles: List[Candle]) -> Tuple[float, float, float]:
        """
        Returns (upper_boundary, lower_boundary, midpoint).
        """
        pass

class IWindowRequirement(ABC):
    """Defines the minimum candle window required to establish a base consolidation."""
    @abstractmethod
    def get_minimum_candles(self) -> int:
        pass

class ICandleContainmentStrategy(ABC):
    """Business strategy for determining whether a candle is contained within a range."""
    
    @abstractmethod
    def is_contained(self, candle: Candle, upper_boundary: float, lower_boundary: float) -> bool:
        """Returns True if the candle satisfies the containment rule."""
        pass

class IConsolidationRepository(ABC):
    """Async, idempotent, INSERT-only repository for Consolidation Snapshots."""
    
    @abstractmethod
    async def save_snapshot(self, snapshot: ConsolidationSnapshot) -> None:
        """Persists the snapshot. Must be idempotent and INSERT-only."""
        pass
        
    @abstractmethod
    async def load_snapshot_by_version(self, snapshot_version: int) -> Optional[ConsolidationSnapshot]:
        """Loads a specific version of a snapshot."""
        pass
        
    @abstractmethod
    async def load_latest_snapshot(self) -> Optional[ConsolidationSnapshot]:
        """Loads the most recently created snapshot."""
        pass
        
    @abstractmethod
    async def load_historical_snapshots(self, limit: int = 10) -> List[ConsolidationSnapshot]:
        """Loads a list of historical snapshots ordered by version descending."""
        pass
        
    @abstractmethod
    async def exists(self, snapshot_version: int) -> bool:
        pass
        
    @abstractmethod
    async def query_by_parent_trend_snapshot(self, parent_version: int) -> List[ConsolidationSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[ConsolidationCandidate]:
        pass
        
    @abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[ConsolidationCandidate]:
        pass

class IConsolidationQueryService(ABC):
    """Service to query consolidations and snapshots without modifying state."""
    
    @abstractmethod
    async def get_latest_snapshot(self) -> Optional[ConsolidationSnapshot]:
        pass
        
    @abstractmethod
    async def get_snapshot_by_version(self, snapshot_version: int) -> Optional[ConsolidationSnapshot]:
        pass
        
    @abstractmethod
    async def get_historical_snapshots(self, limit: int = 10) -> List[ConsolidationSnapshot]:
        pass
        
    @abstractmethod
    async def get_active_consolidations(self, symbol: str, timeframe: str) -> List[ConsolidationCandidate]:
        """Queries the latest snapshot for active consolidations matching symbol and timeframe."""
        pass
