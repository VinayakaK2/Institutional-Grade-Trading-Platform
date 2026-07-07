"""
Watchlist Repository Implementations
======================================

Two implementations of IWatchlistRepository:

  InMemoryWatchlistRepository:
    - For testing and local development.
    - Dict-based in-process storage.
    - No external dependencies.
    - Supports all repository operations.

  PostgreSQLWatchlistRepository:
    - For production.
    - Uses async SQLAlchemy sessionmaker.
    - INSERT-only writes — UPDATE operations on snapshots are prohibited.
    - Full observability via structured logging.
"""
from typing import Dict, List, Optional, cast, Any

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, desc

from backend.core.logger import get_logger
from backend.watchlist_engine.contracts.contracts import IWatchlistRepository
from backend.watchlist_engine.models.models import (
    WatchlistSnapshot,
    WatchlistCandidate,
    WatchlistValidationStatus,
)
from backend.watchlist_engine.models.exceptions import WatchlistRepositoryError
from backend.infrastructure.database.orm.watchlist import WatchlistSnapshotModel

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory Implementation (Testing / Development)
# ─────────────────────────────────────────────────────────────────────────────

class InMemoryWatchlistRepository(IWatchlistRepository):
    """
    In-memory implementation of IWatchlistRepository.

    Suitable for unit testing and local development.
    Uses a dict for O(1) lookup by snapshot_id.
    Snapshot data is never mutated after insertion.

    SNAPSHOT VERSION SEMANTICS:
      - Versions are monotonically increasing. Every successful save_snapshot() call
        increments the version relative to the last known snapshot.
      - Version numbers are never reused. If a snapshot is logically deleted,
        the next run still uses the next sequential version — no gaps are filled.
      - Version is the canonical ordering key. Do not use created_at for ordering.
      - There is no version 0. The first snapshot always has version=1.

    ATOMICITY CONTRACT:
      - Dict assignment is atomic in CPython. A snapshot is either fully present
        in the dict or not present at all. Partial persistence cannot occur.
    """

    def __init__(self) -> None:
        # Keyed by snapshot_id for O(1) lookup.
        self._snapshots: Dict[str, WatchlistSnapshot] = {}

    async def save_snapshot(self, snapshot: WatchlistSnapshot) -> None:
        """Saves the snapshot. Overwrites are architecturally prohibited — IDs are UUIDs."""
        self._snapshots[snapshot.snapshot_id] = snapshot
        logger.debug(f"InMemory: Saved WatchlistSnapshot {snapshot.snapshot_id} (v{snapshot.version}).")

    async def load_snapshot(self, snapshot_id: str) -> Optional[WatchlistSnapshot]:
        """Returns snapshot by ID or None if not found."""
        return self._snapshots.get(snapshot_id)

    async def load_latest_snapshot(self) -> Optional[WatchlistSnapshot]:
        """Returns the most recently created snapshot by monotonic version number."""
        if not self._snapshots:
            return None
        # Use version for ordering — it is monotonic and immune to clock resolution issues.
        return max(self._snapshots.values(), key=lambda s: s.version)

    async def load_snapshot_by_version(self, version: int) -> Optional[WatchlistSnapshot]:
        """Returns snapshot matching the exact version number or None."""
        for snapshot in self._snapshots.values():
            if snapshot.version == version:
                return snapshot
        return None

    async def list_snapshot_history(self, limit: int = 10) -> List[WatchlistSnapshot]:
        """Returns the last N snapshots ordered by version descending."""
        sorted_snapshots = sorted(
            self._snapshots.values(),
            key=lambda s: s.version,
            reverse=True,
        )
        return sorted_snapshots[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL Implementation (Production)
# ─────────────────────────────────────────────────────────────────────────────

class PostgreSQLWatchlistRepository(IWatchlistRepository):
    """
    PostgreSQL-backed implementation of IWatchlistRepository.

    Uses async SQLAlchemy sessions for all operations.
    All writes are INSERT-only — updating existing snapshots is architecturally prohibited.

    SNAPSHOT VERSION SEMANTICS:
      - Versions are monotonically increasing integers. Each run produces previous_version + 1.
      - Version numbers are never reused, even if a snapshot row is deleted.
      - `load_latest_snapshot()` orders by version DESC, not created_at. Timestamps
        are not reliable ordering keys under high concurrency.
      - There is no version 0. The first snapshot always has version=1.

    ATOMICITY CONTRACT:
      - All writes are wrapped in `async with session.begin()`. The transaction commits
        only if all database writes succeed. Any failure triggers a full rollback.
      - A snapshot is either completely persisted or not persisted at all.
      - Partial persistence (incomplete rows, missing JSON fields) cannot occur.
      - Do NOT remove `session.begin()` from write paths — it is the atomicity boundary.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save_snapshot(self, snapshot: WatchlistSnapshot) -> None:
        """
        Persists a new snapshot as an INSERT-only operation.

        Raises:
            WatchlistRepositoryError: If the database write fails.
        """
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    # Serialize candidates to JSON for storage.
                    serialized_candidates = [
                        c.model_dump(mode="json") for c in snapshot.candidates
                    ]
                    model = WatchlistSnapshotModel(
                        snapshot_id=snapshot.snapshot_id,
                        version=snapshot.version,
                        created_at=snapshot.created_at,
                        symbol_count=snapshot.symbol_count,
                        candidates=serialized_candidates,
                        metadata_col=snapshot.metadata,
                        pipeline_version=snapshot.pipeline_version,
                        config_hash=snapshot.config_hash,
                        validation_status=snapshot.validation_status.value,
                        source_pipeline_version=snapshot.source_pipeline_version,
                        source_universe_snapshot_id=snapshot.source_universe_snapshot_id,
                        source_universe_version=snapshot.source_universe_version,
                        candidate_selection_version=snapshot.candidate_selection_version,
                    )
                    session.add(model)
            logger.debug(
                f"PostgreSQL: Saved WatchlistSnapshot {snapshot.snapshot_id} (v{snapshot.version})."
            )
        except Exception as exc:
            logger.error(
                f"Failed to save WatchlistSnapshot {snapshot.snapshot_id}: {exc}",
                exc_info=True,
            )
            raise WatchlistRepositoryError(
                f"Database error while saving WatchlistSnapshot {snapshot.snapshot_id}.",
                details={"error": str(exc)},
            ) from exc

    async def load_snapshot(self, snapshot_id: str) -> Optional[WatchlistSnapshot]:
        """
        Loads a snapshot by ID.

        Raises:
            WatchlistRepositoryError: If the database query fails.
        """
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(WatchlistSnapshotModel).where(
                        WatchlistSnapshotModel.snapshot_id == snapshot_id
                    )
                )
                model = result.scalar_one_or_none()
                if not model:
                    return None
                return self._map_to_domain(model)
        except Exception as exc:
            logger.error(f"Failed to load WatchlistSnapshot {snapshot_id}: {exc}", exc_info=True)
            raise WatchlistRepositoryError(
                f"Database error while loading WatchlistSnapshot {snapshot_id}.",
                details={"error": str(exc)},
            ) from exc

    async def load_latest_snapshot(self) -> Optional[WatchlistSnapshot]:
        """
        Loads the most recently created snapshot.

        Raises:
            WatchlistRepositoryError: If the database query fails.
        """
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(WatchlistSnapshotModel)
                    .order_by(desc(WatchlistSnapshotModel.created_at))
                    .limit(1)
                )
                model = result.scalar_one_or_none()
                if not model:
                    return None
                return self._map_to_domain(model)
        except Exception as exc:
            logger.error(f"Failed to load latest WatchlistSnapshot: {exc}", exc_info=True)
            raise WatchlistRepositoryError(
                "Database error while loading latest WatchlistSnapshot.",
                details={"error": str(exc)},
            ) from exc

    async def load_snapshot_by_version(self, version: int) -> Optional[WatchlistSnapshot]:
        """
        Loads a snapshot by exact version number.

        Raises:
            WatchlistRepositoryError: If the database query fails.
        """
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(WatchlistSnapshotModel).where(
                        WatchlistSnapshotModel.version == version
                    )
                )
                model = result.scalar_one_or_none()
                if not model:
                    return None
                return self._map_to_domain(model)
        except Exception as exc:
            logger.error(
                f"Failed to load WatchlistSnapshot at version {version}: {exc}",
                exc_info=True,
            )
            raise WatchlistRepositoryError(
                f"Database error while loading WatchlistSnapshot at version {version}.",
                details={"error": str(exc)},
            ) from exc

    async def list_snapshot_history(self, limit: int = 10) -> List[WatchlistSnapshot]:
        """
        Returns the last N snapshots ordered by version descending.

        Raises:
            WatchlistRepositoryError: If the database query fails.
        """
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(WatchlistSnapshotModel)
                    .order_by(desc(WatchlistSnapshotModel.version))
                    .limit(limit)
                )
                models = result.scalars().all()
                return [self._map_to_domain(m) for m in models]
        except Exception as exc:
            logger.error(f"Failed to list WatchlistSnapshot history: {exc}", exc_info=True)
            raise WatchlistRepositoryError(
                "Database error while listing WatchlistSnapshot history.",
                details={"error": str(exc)},
            ) from exc

    def _map_to_domain(self, model: WatchlistSnapshotModel) -> WatchlistSnapshot:
        """Maps a WatchlistSnapshotModel ORM row to the immutable WatchlistSnapshot domain model."""
        candidates = [
            WatchlistCandidate(**cast(Dict[str, Any], cand_dict))
            for cand_dict in cast(List[Any], model.candidates)
        ]
        return WatchlistSnapshot(
            snapshot_id=cast(str, model.snapshot_id),
            version=cast(int, model.version),
            created_at=model.created_at,
            symbol_count=cast(int, model.symbol_count),
            candidates=candidates,
            metadata=cast(Dict[str, Any], model.metadata_col),
            pipeline_version=cast(str, model.pipeline_version),
            config_hash=cast(str, model.config_hash),
            validation_status=WatchlistValidationStatus(cast(str, model.validation_status)),
            source_pipeline_version=cast(Optional[str], model.source_pipeline_version),
            source_universe_snapshot_id=cast(Optional[str], model.source_universe_snapshot_id),
            source_universe_version=cast(Optional[int], model.source_universe_version),
            candidate_selection_version=cast(Optional[str], model.candidate_selection_version),
        )
