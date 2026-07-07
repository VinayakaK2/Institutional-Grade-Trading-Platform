from typing import List, Optional, Dict, Any

from backend.watchlist_engine.management.contracts import IManagedWatchlistQueryService, IManagedWatchlistRepository
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistDiff, WatchlistAuditRecord
from backend.watchlist_engine.management.diff_engine import SnapshotDiffEngine

class ManagedWatchlistQueryService(IManagedWatchlistQueryService):
    """
    Read-only query service for managing and diffing snapshots dynamically.
    """
    def __init__(self, repository: IManagedWatchlistRepository, diff_engine: SnapshotDiffEngine):
        self._repository = repository
        self._diff_engine = diff_engine

    async def get_latest_snapshot(self) -> Optional[ManagedWatchlistSnapshot]:
        return await self._repository.load_latest_managed_snapshot()

    async def get_snapshot_by_version(self, version: int) -> Optional[ManagedWatchlistSnapshot]:
        return await self._repository.load_managed_snapshot_by_version(version)

    async def get_snapshot_history(self, limit: int = 100) -> List[ManagedWatchlistSnapshot]:
        return await self._repository.get_snapshot_history(limit=limit)

    async def get_snapshot_diff(self, base_version: Optional[int], target_version: int) -> WatchlistDiff:
        target_snapshot = await self.get_snapshot_by_version(target_version)
        if not target_snapshot:
            raise ValueError(f"Target snapshot version {target_version} not found")
            
        base_snapshot = None
        if base_version is not None:
            base_snapshot = await self.get_snapshot_by_version(base_version)
            if not base_snapshot:
                raise ValueError(f"Base snapshot version {base_version} not found")
                
        return self._diff_engine.compute_diff(target_snapshot, base_snapshot)

    async def get_snapshot_metadata(self, version: int) -> Dict[str, Any]:
        snapshot = await self.get_snapshot_by_version(version)
        if not snapshot:
            return {}
            
        return {
            "managed_snapshot_id": snapshot.managed_snapshot_id,
            "version": snapshot.version,
            "parent_fresh_watchlist_version": snapshot.parent_fresh_watchlist_version,
            "parent_candidate_watchlist_version": snapshot.parent_candidate_watchlist_version,
            "parent_universe_version": snapshot.parent_universe_version,
            "dataset_version": snapshot.dataset_version,
            "pipeline_version": snapshot.pipeline_version,
            "config_hash": snapshot.config_hash,
            "business_fingerprint": snapshot.business_fingerprint,
            "created_at": snapshot.created_at.isoformat(),
            "status": snapshot.status.value,
        }

    async def get_audit_history(self, version: int) -> List[WatchlistAuditRecord]:
        snapshot = await self.get_snapshot_by_version(version)
        if not snapshot:
            return []
            
        return await self._repository.get_audit_history(snapshot.managed_snapshot_id)
