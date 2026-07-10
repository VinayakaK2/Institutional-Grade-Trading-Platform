"""
Trend Engine Repository
=======================

In-memory implementation of the ITrendRepository contract.
Strictly INSERT-only and idempotent.
"""
import asyncio
from typing import List, Optional, Dict

from backend.trend_engine.contracts.contracts import ITrendRepository
from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.exceptions import DuplicateSnapshotVersionError


class InMemoryTrendRepository(ITrendRepository):
    """
    In-memory repository for Trend Snapshots.
    Used for testing, certification, and initial development phases.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        
        # In-memory storage. 
        # _snapshots: list of all snapshots in insertion order.
        # _by_id: index by snapshot_id
        # _by_version: index by snapshot_version
        self._snapshots: List[TrendSnapshot] = []
        self._by_id: Dict[str, TrendSnapshot] = {}
        self._by_version: Dict[int, TrendSnapshot] = {}

    async def save_snapshot(self, snapshot: TrendSnapshot) -> None:
        """
        Persists a new trend snapshot. INSERT-only.
        
        Raises DuplicateSnapshotVersionError if snapshot ID or version already exists.
        """
        async with self._lock:
            if snapshot.snapshot_id in self._by_id:
                raise DuplicateSnapshotVersionError(f"Snapshot with ID {snapshot.snapshot_id} already exists.")
            
            if snapshot.snapshot_version in self._by_version:
                raise DuplicateSnapshotVersionError(f"Snapshot with version {snapshot.snapshot_version} already exists.")
            
            self._snapshots.append(snapshot)
            self._by_id[snapshot.snapshot_id] = snapshot
            self._by_version[snapshot.snapshot_version] = snapshot

    async def load_snapshot(self, snapshot_id: str) -> Optional[TrendSnapshot]:
        """Loads a snapshot by its unique ID."""
        async with self._lock:
            return self._by_id.get(snapshot_id)

    async def load_latest_snapshot(self) -> Optional[TrendSnapshot]:
        """Loads the most recently created snapshot (by version)."""
        async with self._lock:
            if not self._snapshots:
                return None
            return max(self._snapshots, key=lambda s: s.snapshot_version)

    async def load_snapshot_by_version(self, version: int) -> Optional[TrendSnapshot]:
        """Loads a snapshot by its exact version number."""
        async with self._lock:
            return self._by_version.get(version)

    async def list_snapshot_history(self, limit: int = 10) -> List[TrendSnapshot]:
        """Returns the most recent snapshots, ordered by version descending."""
        async with self._lock:
            if not self._snapshots:
                return []
                
            sorted_snapshots = sorted(
                self._snapshots, 
                key=lambda s: s.snapshot_version, 
                reverse=True
            )
            return sorted_snapshots[:limit]
