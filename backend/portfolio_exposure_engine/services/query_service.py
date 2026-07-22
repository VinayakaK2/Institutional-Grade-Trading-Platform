import copy
from typing import List, Optional
from backend.portfolio_exposure_engine.contracts.query_service import IPortfolioExposureQueryService
from backend.portfolio_exposure_engine.repository.memory_repo import MemoryPortfolioExposureRepository
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot

class MemoryPortfolioExposureQueryService(IPortfolioExposureQueryService):
    """
    In-memory projection-oriented read service.
    """
    def __init__(self, repository: MemoryPortfolioExposureRepository):
        self._repository = repository
        
    async def get_latest_exposure(self) -> Optional[PortfolioExposureSnapshot]:
        return await self._repository.latest()
        
    async def get_history(self) -> List[PortfolioExposureSnapshot]:
        async with self._repository._lock:
            sorted_snapshots = sorted(self._repository._store.values(), key=lambda s: s.created_at)
            return [copy.deepcopy(s) for s in sorted_snapshots]
            
    async def query_by_symbol(self, symbol: str) -> List[PortfolioExposureSnapshot]:
        async with self._repository._lock:
            # Filters snapshots where the symbol appears in position exposure
            results = []
            for s in self._repository._store.values():
                if symbol in s.exposure_analysis.position_exposure.individual_weights:
                    results.append(s)
            sorted_snapshots = sorted(results, key=lambda s: s.created_at)
            return [copy.deepcopy(s) for s in sorted_snapshots]
