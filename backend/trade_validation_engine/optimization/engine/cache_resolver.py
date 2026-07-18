from backend.trade_validation_engine.optimization.models.models import CacheResolution
from backend.trade_validation_engine.optimization.contracts.repository import IOptimizationRepository

class OptimizationCacheResolver:
    """
    Interacts with the repository to resolve a fingerprint. 
    Returns a pure CacheResolution object, decoupled from repository models.
    """
    def __init__(self, repository: IOptimizationRepository):
        self._repository = repository

    async def resolve(self, fingerprint: str) -> CacheResolution:
        snapshot = await self._repository.load_by_fingerprint(fingerprint)
        
        if snapshot:
            return CacheResolution(
                cache_hit=True,
                fingerprint=fingerprint,
                snapshot_reference=snapshot.source_trade_decision_snapshot_id,
                cache_reason="Found existing optimization snapshot for fingerprint"
            )
            
        return CacheResolution(
            cache_hit=False,
            fingerprint=fingerprint,
            snapshot_reference=None,
            cache_reason="Cache miss: no snapshot for fingerprint"
        )
