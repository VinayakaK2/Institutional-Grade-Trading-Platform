from abc import ABC, abstractmethod
from typing import Optional, List
from backend.liquidity_grab_engine.optimization.models.models import OptimizationSnapshot

class IOptimizationRepository(ABC):
    @abstractmethod
    async def save(self, snapshot: OptimizationSnapshot) -> None:
        """Saves a fully assembled OptimizationSnapshot."""
        pass
        
    @abstractmethod
    async def exists(self, fingerprint_hash: str) -> bool:
        """Checks if a snapshot exists for the given business fingerprint hash."""
        pass
        
    @abstractmethod
    async def load(self, fingerprint_hash: str) -> Optional[OptimizationSnapshot]:
        """Loads a snapshot by its business fingerprint hash."""
        pass
        
    @abstractmethod
    async def query_by_candidate(self, candidate_id: str) -> List[OptimizationSnapshot]:
        """Loads all snapshots associated with a specific candidate."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[OptimizationSnapshot]:
        """Loads the most recently saved snapshot."""
        pass
