import asyncio
from typing import Optional, List, Dict
from backend.paper_execution_optimization_engine.contracts.repository import IPaperExecutionOptimizationRepository
from backend.paper_execution_optimization_engine.models.snapshot import PaperExecutionOptimizationSnapshot


class OptimizationRepositoryIntegrityError(Exception):
    pass


class OptimizationRepositoryNotFoundError(Exception):
    pass


class OptimizationRepositoryCorruptionError(Exception):
    pass


class MemoryPaperExecutionOptimizationRepository(IPaperExecutionOptimizationRepository):
    """
    In-memory append-only repository.
    """
    def __init__(self):
        self._store: Dict[str, PaperExecutionOptimizationSnapshot] = {}
        self._order: List[str] = []
        self._lock = asyncio.Lock()

    async def save(self, snapshot: PaperExecutionOptimizationSnapshot) -> None:
        async with self._lock:
            if snapshot.optimization_fingerprint in self._store:
                raise OptimizationRepositoryIntegrityError(f"Duplicate INSERT: {snapshot.optimization_fingerprint}")
            self._store[snapshot.optimization_fingerprint] = snapshot
            self._order.append(snapshot.optimization_fingerprint)

    async def save_many(self, snapshots: List[PaperExecutionOptimizationSnapshot]) -> None:
        async with self._lock:
            for snapshot in snapshots:
                if snapshot.optimization_fingerprint in self._store:
                    raise OptimizationRepositoryIntegrityError(f"Duplicate INSERT: {snapshot.optimization_fingerprint}")
            
            for snapshot in snapshots:
                self._store[snapshot.optimization_fingerprint] = snapshot
                self._order.append(snapshot.optimization_fingerprint)

    async def load(self, optimization_fingerprint: str) -> PaperExecutionOptimizationSnapshot:
        async with self._lock:
            if optimization_fingerprint not in self._store:
                raise OptimizationRepositoryNotFoundError(f"Not found: {optimization_fingerprint}")
            return self._store[optimization_fingerprint]

    async def load_latest(self) -> Optional[PaperExecutionOptimizationSnapshot]:
        async with self._lock:
            if not self._order:
                return None
            latest_id = self._order[-1]
            return self._store[latest_id]
