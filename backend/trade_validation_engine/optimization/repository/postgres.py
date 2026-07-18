from typing import Optional, List
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot
from backend.trade_validation_engine.optimization.contracts.repository import IOptimizationRepository

class PostgresOptimizationRepository(IOptimizationRepository):
    """
    PostgreSQL stub for IOptimizationRepository. Raises NotImplementedError.
    """
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    async def save(self, snapshot: OptimizationSnapshot) -> None:
        raise NotImplementedError()

    async def save_many(self, snapshots: List[OptimizationSnapshot]) -> None:
        raise NotImplementedError()

    async def load(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        raise NotImplementedError()

    async def exists(self, optimization_id: str) -> bool:
        raise NotImplementedError()

    async def load_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        raise NotImplementedError()
