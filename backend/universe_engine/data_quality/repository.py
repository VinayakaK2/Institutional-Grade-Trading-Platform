from typing import Optional, Callable
from contextlib import asynccontextmanager

from backend.universe_engine.contracts.data_quality import IDataQualityRepository
from backend.universe_engine.data_quality.models import (
    CertifiedUniverse,
    DataQualityFilterConfiguration,
    DataQualityFilterStatistics,
    DataQualityRejectionDetail,
)
from backend.universe_engine.models.universe import UniverseInstrument
from backend.infrastructure.database.orm.data_quality import CertifiedUniverseModel
from backend.core.logger import get_logger

logger = get_logger(__name__)


class PostgresDataQualityRepository(IDataQualityRepository):
    def __init__(self, session_factory: Callable):
        self.session_factory = session_factory

    @asynccontextmanager
    async def get_session(self):
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def save_certified_universe(self, universe: CertifiedUniverse) -> None:
        async with self.get_session() as session:
            model = CertifiedUniverseModel(
                certified_universe_id=universe.certified_universe_id,
                parent_snapshot_id=universe.parent_snapshot_id,
                pipeline_version=universe.pipeline_version,
                config_hash=universe.config_hash,
                dataset_version=universe.dataset_version,
                created_at=universe.created_at,
                certified_symbols=[
                    inst.model_dump(mode="json") for inst in universe.certified_symbols
                ],
                rejected_symbols=[
                    rej.model_dump(mode="json") for rej in universe.rejected_symbols
                ],
                configuration_snapshot=universe.configuration_snapshot.model_dump(
                    mode="json"
                ),
                statistics=universe.statistics.model_dump(mode="json"),
            )
            session.add(model)
            logger.debug(
                f"Persisted CertifiedUniverse: {universe.certified_universe_id}"
            )

    async def load_certified_universe(
        self, universe_id: str
    ) -> Optional[CertifiedUniverse]:
        async with self.get_session() as session:
            model = await session.get(CertifiedUniverseModel, universe_id)
            if not model:
                return None

            return CertifiedUniverse(
                certified_universe_id=model.certified_universe_id,
                parent_snapshot_id=model.parent_snapshot_id,
                pipeline_version=model.pipeline_version,
                config_hash=model.config_hash,
                dataset_version=model.dataset_version,
                created_at=model.created_at,
                certified_symbols=[
                    UniverseInstrument.model_validate(inst)
                    for inst in model.certified_symbols
                ],
                rejected_symbols=[
                    DataQualityRejectionDetail.model_validate(rej)
                    for rej in model.rejected_symbols
                ],
                configuration_snapshot=DataQualityFilterConfiguration.model_validate(
                    model.configuration_snapshot
                ),
                statistics=DataQualityFilterStatistics.model_validate(model.statistics),
            )


class InMemoryDataQualityRepository(IDataQualityRepository):
    def __init__(self):
        self._storage = {}

    async def save_certified_universe(self, universe: CertifiedUniverse) -> None:
        self._storage[universe.certified_universe_id] = universe

    async def load_certified_universe(
        self, universe_id: str
    ) -> Optional[CertifiedUniverse]:
        return self._storage.get(universe_id)
