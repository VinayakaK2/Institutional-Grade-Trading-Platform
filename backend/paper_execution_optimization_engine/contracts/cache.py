from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot

class ICacheStore(ABC):
    """
    Interface for the cache layer.
    """

    @abstractmethod
    async def resolve(
        self, 
        fingerprint: str, 
        factory_callable: Callable[[], Awaitable[PaperExecutionOptimizationSnapshot]]
    ) -> PaperExecutionOptimizationSnapshot:
        """
        Retrieves the snapshot from cache if it exists, otherwise calls the factory to build it,
        saves it to cache, and returns it.
        
        CRITICAL: The factory_callable MUST be Pure, Deterministic, and Idempotent to guarantee institutional 
        safety against double-execution if executed accidentally.
        """
        pass
    
    @abstractmethod
    async def invalidate(self, fingerprint: str) -> None:
        """
        Invalidates a specific fingerprint from the cache.
        """
        pass

    @abstractmethod
    async def load(self, fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        """
        Loads a snapshot from cache. Raises KeyError if not found.
        """
        pass

    @abstractmethod
    async def save(self, snapshot: PaperExecutionOptimizationSnapshot) -> None:
        """
        Saves a snapshot to cache.
        """
        pass
