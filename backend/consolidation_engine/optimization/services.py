from typing import Optional, List
from backend.consolidation_engine.optimization.contracts import IConsolidationOptimizationRepository
from backend.consolidation_engine.optimization.models import (
    ConsolidationOptimizationSnapshot,
    OptimizationBusinessStatistics,
    OptimizationRuntimeStatistics
)

class ConsolidationOptimizationQueryService:
    """
    Query service for Optimization metadata and statistics.
    Provides decoupled access to repository data.
    """
    
    def __init__(self, repository: IConsolidationOptimizationRepository):
        self.repository = repository
        
    async def latest_optimization_snapshot(self) -> Optional[ConsolidationOptimizationSnapshot]:
        return await self.repository.load_latest()
        
    async def historical_optimization_snapshots(self, parent_id: str) -> List[ConsolidationOptimizationSnapshot]:
        return await self.repository.query_by_parent(parent_id)
        
    async def fingerprint_lookup(self, fingerprint: str) -> Optional[ConsolidationOptimizationSnapshot]:
        return await self.repository.load_by_fingerprint(fingerprint)
        
    async def latest_business_statistics(self) -> Optional[OptimizationBusinessStatistics]:
        latest = await self.latest_optimization_snapshot()
        return latest.business_statistics if latest else None
        
    async def latest_runtime_statistics(self) -> Optional[OptimizationRuntimeStatistics]:
        latest = await self.latest_optimization_snapshot()
        return latest.runtime_statistics if latest else None
