from abc import ABC, abstractmethod
from typing import List, Optional
from backend.consolidation_engine.lifecycle.models import ConsolidationLifecycleSnapshot, ConsolidationLifecycleState

class IConsolidationLifecycleRepository(ABC):
    """
    Contract for immutable, INSERT-only repository for Consolidation Lifecycle Snapshots.
    """
    
    @abstractmethod
    async def save(self, snapshot: ConsolidationLifecycleSnapshot) -> None:
        """Idempotent insert of a lifecycle snapshot."""
        pass
        
    @abstractmethod
    async def exists(self, snapshot_id: str) -> bool:
        """Checks if a snapshot exists by ID."""
        pass
        
    @abstractmethod
    async def load_by_snapshot_id(self, snapshot_id: str) -> Optional[ConsolidationLifecycleSnapshot]:
        """Loads a specific snapshot by its unique ID."""
        pass
        
    @abstractmethod
    async def load_latest(self, candidate_id: str) -> Optional[ConsolidationLifecycleSnapshot]:
        """Loads the most recently generated snapshot for a given candidate."""
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[ConsolidationLifecycleSnapshot]:
        """Loads all snapshots for a symbol."""
        pass
        
    @abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[ConsolidationLifecycleSnapshot]:
        """Loads all snapshots for a given timeframe."""
        pass
        
    @abstractmethod
    async def query_by_state(self, state: ConsolidationLifecycleState) -> List[ConsolidationLifecycleSnapshot]:
        """Loads all snapshots currently at a specific lifecycle state."""
        pass
