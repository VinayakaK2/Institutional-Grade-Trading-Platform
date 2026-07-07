from typing import Optional, Callable

from backend.universe_engine.contracts.liquidity import ILiquidityRepository
from backend.universe_engine.liquidity.models import (
    LiquidityQualifiedUniverse,
    LiquidityFilterConfiguration,
    LiquidityFilterStatistics,
    RejectionDetail
)
from backend.universe_engine.models.universe import UniverseInstrument
from backend.infrastructure.database.orm.liquidity import LiquidityUniverseModel
from backend.core.logger import get_logger
from backend.universe_engine.liquidity.exceptions import LiquidityRepositoryError

logger = get_logger(__name__)

class PostgresLiquidityRepository(ILiquidityRepository):
    """
    PostgreSQL implementation for persisting LiquidityQualifiedUniverse.
    """
    def __init__(self, session_factory: Callable):
        self._session_factory = session_factory

    async def save_liquidity_universe(self, universe: LiquidityQualifiedUniverse) -> None:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    orm_model = LiquidityUniverseModel(
                        liquidity_universe_id=universe.liquidity_universe_id,
                        parent_snapshot_id=universe.parent_snapshot_id,
                        pipeline_version=universe.pipeline_version,
                        config_hash=universe.config_hash,
                        created_at=universe.created_at,
                        qualified_symbols=[sym.model_dump(mode="json") for sym in universe.qualified_symbols],
                        rejected_symbols=[rej.model_dump(mode="json") for rej in universe.rejected_symbols],
                        configuration_snapshot=universe.configuration_snapshot.model_dump(mode="json"),
                        statistics=universe.statistics.model_dump(mode="json")
                    )
                    session.add(orm_model)
            logger.debug(f"Saved LiquidityQualifiedUniverse {universe.liquidity_universe_id} to DB.")
        except Exception as e:
            logger.error(f"Failed to save LiquidityQualifiedUniverse {universe.liquidity_universe_id}: {str(e)}")
            raise LiquidityRepositoryError(f"Database save failed: {str(e)}") from e

    async def load_liquidity_universe(self, universe_id: str) -> Optional[LiquidityQualifiedUniverse]:
        from sqlalchemy.future import select
        try:
            async with self._session_factory() as session:
                stmt = select(LiquidityUniverseModel).where(LiquidityUniverseModel.liquidity_universe_id == universe_id)
                result = await session.execute(stmt)
                orm_model = result.scalar_one_or_none()
                
                if not orm_model:
                    return None
                    
                return LiquidityQualifiedUniverse(
                    liquidity_universe_id=orm_model.liquidity_universe_id,
                    parent_snapshot_id=orm_model.parent_snapshot_id,
                    pipeline_version=orm_model.pipeline_version,
                    config_hash=orm_model.config_hash,
                    created_at=orm_model.created_at,
                    qualified_symbols=[UniverseInstrument(**sym) for sym in orm_model.qualified_symbols],
                    rejected_symbols=[RejectionDetail(**rej) for rej in orm_model.rejected_symbols],
                    configuration_snapshot=LiquidityFilterConfiguration(**orm_model.configuration_snapshot),
                    statistics=LiquidityFilterStatistics(**orm_model.statistics)
                )
        except Exception as e:
            logger.error(f"Failed to load LiquidityQualifiedUniverse {universe_id}: {str(e)}")
            raise LiquidityRepositoryError(f"Database load failed: {str(e)}") from e


class InMemoryLiquidityRepository(ILiquidityRepository):
    """
    In-memory implementation for testing.
    """
    def __init__(self):
        self._store = {}

    async def save_liquidity_universe(self, universe: LiquidityQualifiedUniverse) -> None:
        self._store[universe.liquidity_universe_id] = universe

    async def load_liquidity_universe(self, universe_id: str) -> Optional[LiquidityQualifiedUniverse]:
        return self._store.get(universe_id)
