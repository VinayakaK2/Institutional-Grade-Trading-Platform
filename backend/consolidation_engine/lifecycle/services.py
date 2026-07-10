from typing import List, Optional
from backend.consolidation_engine.lifecycle.contracts import IConsolidationLifecycleRepository
from backend.consolidation_engine.lifecycle.models import ConsolidationLifecycleSnapshot, ConsolidationLifecycleState

class ConsolidationLifecycleQueryService:
    """
    Query service for Consolidation Lifecycle Snapshots.
    Provides decoupled access to repository data.
    """
    
    def __init__(self, repository: IConsolidationLifecycleRepository):
        self.repository = repository
        
    async def latest_lifecycle_snapshot(self, candidate_id: str) -> Optional[ConsolidationLifecycleSnapshot]:
        return await self.repository.load_latest(candidate_id)
        
    async def historical_lifecycle_snapshots(self, candidate_id: str) -> List[ConsolidationLifecycleSnapshot]:
        """
        Loads all snapshots for a given candidate, ideally sorted chronologically.
        Since we don't have a direct query in the stub repository interface for all by candidate,
        this would require an expanded repository interface for a full implementation.
        """
        # For Phase 8.4 boundaries, we can return empty or extend the repo.
        return []
        
    async def active_consolidations(self, symbol: Optional[str] = None) -> List[ConsolidationLifecycleSnapshot]:
        """Returns all snapshots that are currently ACTIVE."""
        snapshots = await self.repository.query_by_state(ConsolidationLifecycleState.ACTIVE)
        if symbol:
            snapshots = [s for s in snapshots if s.symbol == symbol]
        return snapshots
        
    async def broken_consolidations(self, symbol: Optional[str] = None) -> List[ConsolidationLifecycleSnapshot]:
        """Returns all snapshots that are currently BROKEN."""
        snapshots = await self.repository.query_by_state(ConsolidationLifecycleState.BROKEN)
        if symbol:
            snapshots = [s for s in snapshots if s.symbol == symbol]
        return snapshots
        
    async def ended_consolidations(self, symbol: Optional[str] = None) -> List[ConsolidationLifecycleSnapshot]:
        """Returns all snapshots that are currently ENDED."""
        snapshots = await self.repository.query_by_state(ConsolidationLifecycleState.ENDED)
        if symbol:
            snapshots = [s for s in snapshots if s.symbol == symbol]
        return snapshots
