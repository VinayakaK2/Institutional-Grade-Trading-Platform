"""
Optimization Engine Decorator
=============================

Decorates IWatchlistEngine to provide full-bypass incremental processing.
"""
from typing import List, Optional

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistEngine, IWatchlistRepository
from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistResult
from backend.watchlist_engine.models.config import WatchlistOptimizationSettings
from backend.watchlist_engine.optimization.fingerprint import OptimizationFingerprintBuilder

logger = get_logger(__name__)


class WatchlistOptimizationEngine(IWatchlistEngine):
    """
    Decorator for IWatchlistEngine.
    
    If the business fingerprint of the incoming request exactly matches the latest snapshot,
    this engine bypasses execution entirely and returns the existing snapshot.
    """
    
    def __init__(
        self, 
        inner: IWatchlistEngine, 
        settings: WatchlistOptimizationSettings,
        repository: IWatchlistRepository
    ):
        self._inner = inner
        self._settings = settings
        self._repository = repository

    async def generate_watchlist(
        self,
        run_id: str,
        candidates: List[WatchlistCandidate],
        source_universe_snapshot_id: Optional[str] = None,
        source_universe_version: Optional[int] = None,
        config_hash: str = "unknown",
        candidate_selection_version: Optional[str] = None
    ) -> WatchlistResult:
        
        if not self._settings.enable_incremental_processing:
            logger.info("Incremental processing disabled. Calling inner engine.")
            return await self._inner.generate_watchlist(
                run_id=run_id,
                candidates=candidates,
                source_universe_snapshot_id=source_universe_snapshot_id,
                source_universe_version=source_universe_version,
                config_hash=config_hash,
                candidate_selection_version=candidate_selection_version
            )
            
        # 1. Compute Business Fingerprint
        # Since dataset_version isn't natively passed through generate_watchlist (unless baked into config_hash),
        # we use config_hash and the candidates themselves to represent the business state.
        fingerprint = OptimizationFingerprintBuilder.build(
            dataset_version="n/a",  # Expected to be encapsulated in config_hash or not applicable
            config_hash=config_hash,
            candidates=candidates
        )
        
        # 2. Load latest snapshot to check fingerprint
        latest_snapshot = await self._repository.load_latest_snapshot()
        
        if latest_snapshot and latest_snapshot.metadata.get("optimization_fingerprint") == fingerprint:
            logger.info(f"Optimization bypass triggered! Fingerprint {fingerprint} matches latest snapshot. Returning unchanged snapshot {latest_snapshot.snapshot_id}.")
            # Return the previous snapshot without executing anything
            return WatchlistResult(snapshot=latest_snapshot)
            
        # 3. Fingerprint mismatch - delegate to inner engine
        logger.info(f"Fingerprint {fingerprint} does not match latest snapshot. Triggering inner engine execution.")
        result = await self._inner.generate_watchlist(
            run_id=run_id,
            candidates=candidates,
            source_universe_snapshot_id=source_universe_snapshot_id,
            source_universe_version=source_universe_version,
            config_hash=config_hash,
            candidate_selection_version=candidate_selection_version,
            metadata_overrides={"optimization_fingerprint": fingerprint}
        )
        
        return result
