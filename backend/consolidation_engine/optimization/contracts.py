from abc import ABC, abstractmethod
from typing import Optional, List
from backend.consolidation_engine.optimization.models import (
    ConsolidationOptimizationSnapshot,
    ConsolidationProcessingRequest,
    ConsolidationProcessingResult
)

class IConsolidationProcessor(ABC):
    """
    Domain-aware interface for processing consolidation logic.
    Implemented by underlying engines (e.g. Lifecycle Engine).
    """
    @abstractmethod
    async def process(self, request: ConsolidationProcessingRequest) -> ConsolidationProcessingResult:
        pass


class IConsolidationOptimizationRepository(ABC):
    """
    Contract for immutable, INSERT-only repository for Consolidation Optimization Snapshots.
    """
    
    @abstractmethod
    async def save(self, snapshot: ConsolidationOptimizationSnapshot) -> None:
        """Idempotent insert of an optimization snapshot."""
        pass
        
    @abstractmethod
    async def exists(self, fingerprint: str) -> bool:
        """Checks if a snapshot exists by fingerprint."""
        pass
        
    @abstractmethod
    async def load_by_fingerprint(self, fingerprint: str) -> Optional[ConsolidationOptimizationSnapshot]:
        """Loads a specific optimization snapshot by its business fingerprint."""
        pass
        
    @abstractmethod
    async def load_latest(self) -> Optional[ConsolidationOptimizationSnapshot]:
        """Loads the most recently generated optimization snapshot."""
        pass
        
    @abstractmethod
    async def query_by_parent(self, parent_id: str) -> List[ConsolidationOptimizationSnapshot]:
        """Loads snapshots that derived from a parent snapshot."""
        pass
        
    @abstractmethod
    async def get_cached_result(self, fingerprint: str) -> Optional[ConsolidationProcessingResult]:
        """
        Retrieves a previously computed processing result using the business fingerprint.
        This represents the actual 'cache hit' behavior.
        """
        pass
        
    @abstractmethod
    async def save_cached_result(self, result: ConsolidationProcessingResult) -> None:
        """
        Saves a freshly computed processing result against its business fingerprint.
        """
        pass
