from typing import Optional, Dict
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from backend.universe_engine.contracts.repository import IUniverseRepository
from backend.universe_engine.models.universe import UniverseSnapshot, ValidationStatus, UniverseInstrument
from backend.infrastructure.database.orm.universe import UniverseSnapshotModel
from backend.universe_engine.models.exceptions import UniverseRepositoryError
from backend.core.logger import get_logger

logger = get_logger(__name__)

class PostgreSQLUniverseRepository(IUniverseRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save_snapshot(self, snapshot: UniverseSnapshot) -> None:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    # Serialize instruments to JSON
                    serialized_instruments = [inst.model_dump(mode="json") for inst in snapshot.instruments]
                    
                    model = UniverseSnapshotModel(
                        snapshot_id=snapshot.snapshot_id,
                        version=snapshot.version,
                        provider=snapshot.provider,
                        created_at=snapshot.created_at,
                        symbol_count=snapshot.symbol_count,
                        instruments=serialized_instruments,
                        metadata_col=snapshot.metadata,
                        pipeline_version=snapshot.pipeline_version,
                        validation_status=snapshot.validation_status.value
                    )
                    session.add(model)
                logger.debug(f"Saved UniverseSnapshot {snapshot.snapshot_id} to database.")
        except Exception as e:
            logger.error(f"Failed to save UniverseSnapshot {snapshot.snapshot_id}: {e}", exc_info=True)
            raise UniverseRepositoryError(f"Database error while saving snapshot {snapshot.snapshot_id}", details={"error": str(e)}) from e

    async def load_snapshot(self, snapshot_id: str) -> Optional[UniverseSnapshot]:
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(UniverseSnapshotModel).where(UniverseSnapshotModel.snapshot_id == snapshot_id)
                )
                model = result.scalar_one_or_none()
                
                if not model:
                    return None
                    
                return self._map_to_domain(model)
        except Exception as e:
            logger.error(f"Failed to load UniverseSnapshot {snapshot_id}: {e}", exc_info=True)
            raise UniverseRepositoryError(f"Database error while loading snapshot {snapshot_id}", details={"error": str(e)}) from e

    async def load_latest_snapshot(self) -> Optional[UniverseSnapshot]:
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    select(UniverseSnapshotModel)
                    .order_by(desc(UniverseSnapshotModel.created_at))
                    .limit(1)
                )
                model = result.scalar_one_or_none()
                
                if not model:
                    return None
                    
                return self._map_to_domain(model)
        except Exception as e:
            logger.error(f"Failed to load latest UniverseSnapshot: {e}", exc_info=True)
            raise UniverseRepositoryError("Database error while loading latest snapshot", details={"error": str(e)}) from e

    def _map_to_domain(self, model: UniverseSnapshotModel) -> UniverseSnapshot:
        instruments = [UniverseInstrument(**inst_dict) for inst_dict in model.instruments]
        return UniverseSnapshot(
            snapshot_id=model.snapshot_id,
            version=model.version,
            provider=model.provider,
            created_at=model.created_at,
            symbol_count=model.symbol_count,
            instruments=instruments,
            metadata=model.metadata_col,
            pipeline_version=model.pipeline_version,
            validation_status=ValidationStatus(model.validation_status)
        )

class InMemoryUniverseRepository(IUniverseRepository):
    def __init__(self):
        self._snapshots: Dict[str, UniverseSnapshot] = {}

    async def save_snapshot(self, snapshot: UniverseSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot

    async def load_snapshot(self, snapshot_id: str) -> Optional[UniverseSnapshot]:
        return self._snapshots.get(snapshot_id)

    async def load_latest_snapshot(self) -> Optional[UniverseSnapshot]:
        if not self._snapshots:
            return None
        # Return the one with latest created_at
        return max(self._snapshots.values(), key=lambda x: x.created_at)
