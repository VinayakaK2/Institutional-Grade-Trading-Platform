import abc
from typing import Optional
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot

class IOptimizationQueryService(abc.ABC):
    """
    Read-only queries for OptimizationSnapshot.
    """
    @abc.abstractmethod
    async def get_by_optimization_id(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        pass

    @abc.abstractmethod
    async def get_latest(self) -> Optional[OptimizationSnapshot]:
        pass

    @abc.abstractmethod
    async def get_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        pass
