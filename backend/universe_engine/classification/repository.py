from typing import Optional, Dict
from sqlalchemy import select

from backend.universe_engine.contracts.classification import IUniverseClassificationRepository
from backend.universe_engine.classification.models import ClassifiedUniverse
from backend.infrastructure.database.orm.classification import ClassifiedUniverseModel

class InMemoryClassificationRepository(IUniverseClassificationRepository):
    def __init__(self):
        self._storage: Dict[str, ClassifiedUniverse] = {}

    async def save_classified_universe(self, universe: ClassifiedUniverse) -> None:
        self._storage[universe.classified_universe_id] = universe

    async def load_classified_universe(self, universe_id: str) -> Optional[ClassifiedUniverse]:
        return self._storage.get(universe_id)


class PostgresClassificationRepository(IUniverseClassificationRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def save_classified_universe(self, universe: ClassifiedUniverse) -> None:
        async with self._session_factory() as session:
            model = ClassifiedUniverseModel(
                classified_universe_id=universe.classified_universe_id,
                parent_certified_universe_id=universe.parent_certified_universe_id,
                pipeline_version=universe.pipeline_version,
                config_hash=universe.config_hash,
                classified_symbols=[s.model_dump() for s in universe.classified_symbols],
                configuration_snapshot=universe.configuration_snapshot.model_dump(),
                statistics=universe.statistics.model_dump()
            )
            session.add(model)
            await session.commit()

    async def load_classified_universe(self, universe_id: str) -> Optional[ClassifiedUniverse]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ClassifiedUniverseModel).where(ClassifiedUniverseModel.classified_universe_id == universe_id)
            )
            model = result.scalars().first()
            if not model:
                return None

            return ClassifiedUniverse(
                classified_universe_id=model.classified_universe_id,
                parent_certified_universe_id=model.parent_certified_universe_id,
                pipeline_version=model.pipeline_version,
                config_hash=model.config_hash,
                created_at=model.created_at,
                classified_symbols=model.classified_symbols,
                configuration_snapshot=model.configuration_snapshot,
                statistics=model.statistics
            )
