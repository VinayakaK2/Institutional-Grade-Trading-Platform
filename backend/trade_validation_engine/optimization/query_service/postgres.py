from typing import Optional
from backend.trade_validation_engine.optimization.models.models import OptimizationSnapshot
from backend.trade_validation_engine.optimization.contracts.query_service import IOptimizationQueryService

class PostgresOptimizationQueryService(IOptimizationQueryService):
    """
    PostgreSQL stub for IOptimizationQueryService. Raises NotImplementedError.
    """
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    async def get_by_optimization_id(self, optimization_id: str) -> Optional[OptimizationSnapshot]:
        raise NotImplementedError()

    async def get_latest(self) -> Optional[OptimizationSnapshot]:
        raise NotImplementedError()

    async def get_by_fingerprint(self, fingerprint: str) -> Optional[OptimizationSnapshot]:
        raise NotImplementedError()
