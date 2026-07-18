from typing import Optional
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot
from backend.trade_validation_engine.optimization.contracts.query_service import IOptimizationQueryService
from backend.trade_validation_engine.optimization.repository.memory import InMemoryOptimizationRepository

class InMemoryOptimizationQueryService(IOptimizationQueryService):
    """
    Read-only memory query service for OptimizationSnapshot.
    """
    def __init__(self, repository: InMemoryOptimizationRepository) -> None:
        self._repository = repository

    async def get_by_optimization_id(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        return await self._repository.load(optimization_id)

    async def get_latest(self) -> Optional[OptimizationSnapshot]:
        if not self._repository._storage:
            return None
        # In memory, we just return the last added
        return list(self._repository._storage.values())[-1]

    async def get_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        return await self._repository.load_by_fingerprint(fingerprint)
