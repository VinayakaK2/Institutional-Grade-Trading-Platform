"""
Fresh Watchlist Repository
==========================

Implements IFreshWatchlistRepository.
"""
from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.watchlist_engine.freshness.contracts import IFreshWatchlistRepository
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.freshness.infrastructure.orm import FreshWatchlistSnapshotModel
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from backend.watchlist_engine.repository.repository import PostgreSQLWatchlistRepository


class FreshWatchlistRepository(IFreshWatchlistRepository):
    """
    SQLAlchemy implementation for the Fresh Watchlist Repository.
    """
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save_fresh_snapshot(self, snapshot: FreshWatchlistSnapshot) -> None:
        """Persists a new fresh watchlist snapshot."""
        model = FreshWatchlistSnapshotModel(
            freshness_snapshot_id=snapshot.freshness_snapshot_id,
            version=snapshot.version,
            watchlist_snapshot_id=snapshot.watchlist_snapshot.snapshot_id,
            dataset_version=snapshot.dataset_version,
            parent_candidate_watchlist_version=snapshot.parent_candidate_watchlist_version
        )
        
        async with self._session_factory() as session:
            session.add(model)
            await session.commit()

    async def load_latest_fresh_snapshot(self) -> Optional[FreshWatchlistSnapshot]:
        """Loads the most recently created fresh snapshot."""
        async with self._session_factory() as session:
            stmt = (
                select(FreshWatchlistSnapshotModel)
                .options(selectinload(FreshWatchlistSnapshotModel.watchlist_snapshot))
                .order_by(desc(FreshWatchlistSnapshotModel.version))
                .limit(1)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return None
                
            # Use the foundation repository's mapping logic to hydrate WatchlistSnapshot
            watchlist_snapshot = PostgreSQLWatchlistRepository._map_to_domain(model.watchlist_snapshot)
            
            return FreshWatchlistSnapshot(
                freshness_snapshot_id=model.freshness_snapshot_id,
                version=model.version,
                watchlist_snapshot=watchlist_snapshot,
                dataset_version=model.dataset_version,
                parent_candidate_watchlist_version=model.parent_candidate_watchlist_version
            )

    async def load_fresh_snapshot_by_version(self, version: int) -> Optional[FreshWatchlistSnapshot]:
        """Loads a fresh snapshot by its exact version number."""
        async with self._session_factory() as session:
            stmt = (
                select(FreshWatchlistSnapshotModel)
                .options(selectinload(FreshWatchlistSnapshotModel.watchlist_snapshot))
                .where(FreshWatchlistSnapshotModel.version == version)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return None
                
            watchlist_snapshot = PostgreSQLWatchlistRepository._map_to_domain(model.watchlist_snapshot)
            
            return FreshWatchlistSnapshot(
                freshness_snapshot_id=model.freshness_snapshot_id,
                version=model.version,
                watchlist_snapshot=watchlist_snapshot,
                dataset_version=model.dataset_version,
                parent_candidate_watchlist_version=model.parent_candidate_watchlist_version
            )
