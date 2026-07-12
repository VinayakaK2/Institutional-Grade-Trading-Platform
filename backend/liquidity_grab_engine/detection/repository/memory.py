from typing import List, Optional, Dict
from backend.liquidity_grab_engine.detection.contracts.repository import ILiquidityGrabDetectionRepository
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate

class InMemoryDetectionRepository(ILiquidityGrabDetectionRepository):
    """
    In-Memory implementation of the ILiquidityGrabDetectionRepository.
    Used for testing and determinism verification.
    """
    def __init__(self) -> None:
        self._candidates: Dict[str, LiquidityGrabCandidate] = {}
        
    async def save(self, candidate: LiquidityGrabCandidate) -> None:
        self._candidates[candidate.candidate_id] = candidate

    async def load(self, candidate_id: str) -> Optional[LiquidityGrabCandidate]:
        return self._candidates.get(candidate_id)

    async def exists(self, candidate_id: str) -> bool:
        return candidate_id in self._candidates

    async def query_by_symbol(self, symbol_id: str) -> List[LiquidityGrabCandidate]:
        return [c for c in self._candidates.values() if c.symbol_id == symbol_id]

    async def query_by_timeframe(self, timeframe: str) -> List[LiquidityGrabCandidate]:
        return [c for c in self._candidates.values() if c.timeframe == timeframe]

    async def query_by_parent_trend_snapshot(self, snapshot_version: int) -> List[LiquidityGrabCandidate]:
        return [c for c in self._candidates.values() if c.parent_trend_snapshot_version == snapshot_version]

    async def query_by_parent_consolidation_snapshot(self, snapshot_version: int) -> List[LiquidityGrabCandidate]:
        return [c for c in self._candidates.values() if c.parent_consolidation_snapshot_version == snapshot_version]
        
    async def query_by_dataset_version(self, dataset_version: int) -> List[LiquidityGrabCandidate]:
        return [c for c in self._candidates.values() if c.dataset_version == dataset_version]

    async def load_latest(self) -> Optional[LiquidityGrabCandidate]:
        if not self._candidates:
            return None
        # Return the candidate with the most recent created_timestamp
        return max(self._candidates.values(), key=lambda c: c.metadata.created_timestamp)
