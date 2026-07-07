from typing import List, Optional

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.database.orm.watchlist import WatchlistSnapshotModel
from backend.watchlist_engine.freshness.infrastructure.orm import FreshWatchlistSnapshotModel
from backend.watchlist_engine.management.infrastructure.orm import ManagedWatchlistSnapshotModel, WatchlistAuditRecordModel
from backend.infrastructure.database.exceptions import InfrastructureException, DatabaseIntegrityException
from backend.watchlist_engine.management.contracts import IManagedWatchlistRepository
from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistAuditRecord, WatchlistStatus
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.watchlist_engine.models.models import WatchlistSnapshot, WatchlistValidationStatus, WatchlistCandidate

class ManagedWatchlistRepository(IManagedWatchlistRepository):
    """
    INSERT-only repository for ManagedWatchlistSnapshot and AuditRecords.
    """
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def save_managed_snapshot(self, snapshot: ManagedWatchlistSnapshot, audit_record: WatchlistAuditRecord) -> None:
        async with self._session_factory() as session:
            try:
                # Check for duplicate version
                stmt = select(ManagedWatchlistSnapshotModel).where(
                    ManagedWatchlistSnapshotModel.version == snapshot.version
                )
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    raise DatabaseIntegrityException(f"ManagedWatchlistSnapshot version {snapshot.version} already exists")

                orm_snapshot = ManagedWatchlistSnapshotModel(
                    managed_snapshot_id=snapshot.managed_snapshot_id,
                    version=snapshot.version,
                    fresh_snapshot_id=snapshot.fresh_watchlist_snapshot.freshness_snapshot_id,
                    parent_fresh_watchlist_version=snapshot.parent_fresh_watchlist_version,
                    parent_candidate_watchlist_version=snapshot.parent_candidate_watchlist_version,
                    parent_universe_version=snapshot.parent_universe_version,
                    dataset_version=snapshot.dataset_version,
                    pipeline_version=snapshot.pipeline_version,
                    config_hash=snapshot.config_hash,
                    business_fingerprint=snapshot.business_fingerprint,
                    status=snapshot.status.value,
                    created_at=snapshot.created_at
                )
                
                orm_audit = WatchlistAuditRecordModel(
                    event_id=audit_record.event_id,
                    managed_snapshot_id=audit_record.managed_snapshot_id,
                    event_type=audit_record.event_type,
                    timestamp=audit_record.timestamp,
                    metadata_payload=audit_record.metadata
                )
                
                session.add(orm_snapshot)
                session.add(orm_audit)
                await session.commit()
            except DatabaseIntegrityException:
                await session.rollback()
                raise
            except Exception as e:
                await session.rollback()
                raise DatabaseIntegrityException(f"Failed to save managed watchlist snapshot: {str(e)}") from e

    async def load_latest_managed_snapshot(self) -> Optional[ManagedWatchlistSnapshot]:
        async with self._session_factory() as session:
            try:
                stmt = select(ManagedWatchlistSnapshotModel).order_by(
                    ManagedWatchlistSnapshotModel.version.desc()
                ).limit(1)
                
                result = await session.execute(stmt)
                orm_snapshot = result.scalar_one_or_none()
                
                if not orm_snapshot:
                    return None
                    
                return await self._to_domain(session, orm_snapshot)
            except Exception as e:
                raise DatabaseIntegrityException(f"Failed to load latest managed snapshot: {str(e)}") from e

    async def load_managed_snapshot_by_version(self, version: int) -> Optional[ManagedWatchlistSnapshot]:
        async with self._session_factory() as session:
            try:
                stmt = select(ManagedWatchlistSnapshotModel).where(
                    ManagedWatchlistSnapshotModel.version == version
                )
                
                result = await session.execute(stmt)
                orm_snapshot = result.scalar_one_or_none()
                
                if not orm_snapshot:
                    return None
                    
                return await self._to_domain(session, orm_snapshot)
            except Exception as e:
                raise DatabaseIntegrityException(f"Failed to load managed snapshot {version}: {str(e)}") from e

    async def get_snapshot_history(self, limit: int = 100) -> List[ManagedWatchlistSnapshot]:
        async with self._session_factory() as session:
            try:
                stmt = select(ManagedWatchlistSnapshotModel).order_by(
                    ManagedWatchlistSnapshotModel.version.desc()
                ).limit(limit)
                
                result = await session.execute(stmt)
                orm_snapshots = result.scalars().all()
                
                domain_snapshots = []
                for orm_snapshot in orm_snapshots:
                    domain_snapshots.append(await self._to_domain(session, orm_snapshot))
                return domain_snapshots
            except Exception as e:
                raise InfrastructureException(f"Failed to load snapshot history: {str(e)}") from e

    async def get_audit_history(self, managed_snapshot_id: str) -> List[WatchlistAuditRecord]:
        async with self._session_factory() as session:
            try:
                stmt = select(WatchlistAuditRecordModel).where(
                    WatchlistAuditRecordModel.managed_snapshot_id == managed_snapshot_id
                ).order_by(WatchlistAuditRecordModel.timestamp.desc())
                
                result = await session.execute(stmt)
                orm_audits = result.scalars().all()
                
                return [
                    WatchlistAuditRecord(
                        event_id=a.event_id,
                        managed_snapshot_id=a.managed_snapshot_id,
                        event_type=a.event_type,
                        timestamp=a.timestamp,
                        metadata=a.metadata_payload
                    )
                    for a in orm_audits
                ]
            except Exception as e:
                raise InfrastructureException(f"Failed to load audit history: {str(e)}") from e

    async def _to_domain(self, session: AsyncSession, orm_managed: ManagedWatchlistSnapshotModel) -> ManagedWatchlistSnapshot:
        # Load the inner fresh snapshot
        stmt = select(FreshWatchlistSnapshotModel).where(
            FreshWatchlistSnapshotModel.freshness_snapshot_id == orm_managed.fresh_snapshot_id
        )
        result = await session.execute(stmt)
        orm_fresh = result.scalar_one_or_none()
        
        if not orm_fresh:
            raise InfrastructureException(f"Data corruption: missing fresh snapshot {orm_managed.fresh_snapshot_id}")
            
        # Load the innermost watchlist snapshot
        stmt2 = select(WatchlistSnapshotModel).where(
            WatchlistSnapshotModel.snapshot_id == orm_fresh.watchlist_snapshot_id
        )
        result2 = await session.execute(stmt2)
        orm_base = result2.scalar_one_or_none()
        
        if not orm_base:
            raise InfrastructureException(f"Data corruption: missing base snapshot {orm_fresh.watchlist_snapshot_id}")
            
        base_snapshot = WatchlistSnapshot(
            snapshot_id=orm_base.snapshot_id,
            version=orm_base.version,
            created_at=orm_base.created_at,
            symbol_count=orm_base.symbol_count,
            candidates=[WatchlistCandidate.model_validate(c) for c in orm_base.candidates],
            metadata=orm_base.metadata_col,
            pipeline_version=orm_base.pipeline_version,
            candidate_selection_version=orm_base.candidate_selection_version,
            config_hash=orm_base.config_hash,
            validation_status=WatchlistValidationStatus(orm_base.validation_status),
            source_pipeline_version=orm_base.source_pipeline_version,
            source_universe_snapshot_id=orm_base.source_universe_snapshot_id,
            source_universe_version=orm_base.source_universe_version
        )
        
        fresh_snapshot = FreshWatchlistSnapshot(
            freshness_snapshot_id=orm_fresh.freshness_snapshot_id,
            version=orm_fresh.version,
            watchlist_snapshot=base_snapshot,
            dataset_version=orm_fresh.dataset_version,
            parent_candidate_watchlist_version=orm_fresh.parent_candidate_watchlist_version
        )
        
        return ManagedWatchlistSnapshot(
            managed_snapshot_id=orm_managed.managed_snapshot_id,
            version=orm_managed.version,
            fresh_watchlist_snapshot=fresh_snapshot,
            parent_fresh_watchlist_version=orm_managed.parent_fresh_watchlist_version,
            parent_candidate_watchlist_version=orm_managed.parent_candidate_watchlist_version,
            parent_universe_version=orm_managed.parent_universe_version,
            dataset_version=orm_managed.dataset_version,
            pipeline_version=orm_managed.pipeline_version,
            config_hash=orm_managed.config_hash,
            business_fingerprint=orm_managed.business_fingerprint,
            created_at=orm_managed.created_at,
            status=WatchlistStatus(orm_managed.status)
        )
