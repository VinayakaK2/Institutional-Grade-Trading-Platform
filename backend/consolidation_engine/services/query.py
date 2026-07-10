from typing import List, Optional

from backend.consolidation_engine.models.models import ConsolidationSnapshot, ConsolidationCandidate
from backend.consolidation_engine.contracts.contracts import IConsolidationQueryService, IConsolidationRepository

class ConsolidationQueryService(IConsolidationQueryService):
    """
    Service to query consolidations and snapshots safely without modifying state.
    """
    
    def __init__(self, repository: IConsolidationRepository):
        self._repository = repository
        
    async def get_latest_snapshot(self) -> Optional[ConsolidationSnapshot]:
        return await self._repository.load_latest_snapshot()
        
    async def get_snapshot_by_version(self, snapshot_version: int) -> Optional[ConsolidationSnapshot]:
        return await self._repository.load_snapshot_by_version(snapshot_version)
        
    async def get_historical_snapshots(self, limit: int = 10) -> List[ConsolidationSnapshot]:
        return await self._repository.load_historical_snapshots(limit)
        
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[ConsolidationCandidate]:
        """
        Retrieves a candidate by its unique ID from the latest snapshot.
        If optimization/caching exists across historical snapshots, this can be expanded.
        """
        snapshot = await self.get_latest_snapshot()
        if not snapshot:
            return None
            
        for candidate in snapshot.candidates:
            if candidate.candidate_id == candidate_id:
                return candidate
                
        return None
        
    async def get_active_consolidations(self, symbol: str, timeframe: str) -> List[ConsolidationCandidate]:
        """
        Queries the latest snapshot for active consolidations matching symbol and timeframe.
        """
        snapshot = await self.get_latest_snapshot()
        if not snapshot:
            return []
            
        return [
            candidate for candidate in snapshot.candidates
            if candidate.symbol == symbol and candidate.timeframe == timeframe
        ]
