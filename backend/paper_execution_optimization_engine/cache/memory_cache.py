from typing import Dict, Callable, Awaitable, TypeVar
import asyncio
from backend.paper_execution_optimization_engine.contracts.cache import ICacheStore
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot

T = TypeVar('T', bound=PaperExecutionOptimizationSnapshot)

class MemoryCacheStore(ICacheStore):
    """
    In-memory implementation of ICacheStore.
    """
    def __init__(self):
        self._store: Dict[str, PaperExecutionOptimizationSnapshot] = {}
        self._lock = asyncio.Lock()

    async def resolve(
        self, 
        fingerprint: str, 
        factory_callable: Callable[[], Awaitable[T]]
    ) -> T:
        async with self._lock:
            if fingerprint in self._store:
                return self._store[fingerprint] # type: ignore
                
            # If not in cache, call factory (idempotent)
            snapshot = await factory_callable()
            self._store[fingerprint] = snapshot
            return snapshot
            
    async def save(self, snapshot: PaperExecutionOptimizationSnapshot) -> None:
        async with self._lock:
            self._store[snapshot.optimization_fingerprint] = snapshot

    async def load(self, fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        async with self._lock:
            if fingerprint not in self._store:
                raise KeyError(f"Cache miss for fingerprint: {fingerprint}")
            return self._store[fingerprint]

    async def invalidate(self, fingerprint: str) -> None:
        async with self._lock:
            if fingerprint in self._store:
                del self._store[fingerprint]
