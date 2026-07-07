from sqlalchemy import select
from backend.universe_engine.contracts.optimization import IUniverseOptimizationRepository
from backend.universe_engine.optimization.models import (
    OptimizedUniverse,
    OptimizationMetrics,
    UniverseOptimizationConfiguration
)
from backend.infrastructure.database.orm.optimization import OptimizedUniverseModel

class PostgresOptimizationRepository(IUniverseOptimizationRepository):
    """
    PostgreSQL implementation of the optimization repository.
    """
    def __init__(self, async_session_factory):
        self._async_session_factory = async_session_factory

    async def save_optimized_universe(self, universe: OptimizedUniverse) -> None:
        async with self._async_session_factory() as session:
            async with session.begin():
                db_model = OptimizedUniverseModel(
                    optimized_universe_id=universe.optimized_universe_id,
                    parent_classified_universe_id=universe.parent_classified_universe_id,
                    previous_optimized_universe_id=universe.previous_optimized_universe_id,
                    pipeline_version=universe.pipeline_version,
                    config_hash=universe.config_hash,
                    created_at=universe.created_at,
                    configuration_snapshot=universe.configuration_snapshot.model_dump(),
                    optimization_metrics=universe.optimization_metrics.model_dump(),
                    symbol_fingerprints=universe.symbol_fingerprints
                )
                session.add(db_model)

    async def load_optimized_universe(self, optimized_universe_id: str) -> OptimizedUniverse:
        async with self._async_session_factory() as session:
            stmt = select(OptimizedUniverseModel).where(
                OptimizedUniverseModel.optimized_universe_id == optimized_universe_id
            )
            result = await session.execute(stmt)
            db_model = result.scalar_one_or_none()
            
            if db_model is None:
                raise ValueError(f"OptimizedUniverse {optimized_universe_id} not found")
                
            return OptimizedUniverse(
                optimized_universe_id=db_model.optimized_universe_id,
                parent_classified_universe_id=db_model.parent_classified_universe_id,
                previous_optimized_universe_id=db_model.previous_optimized_universe_id,
                pipeline_version=db_model.pipeline_version,
                config_hash=db_model.config_hash,
                created_at=db_model.created_at,
                configuration_snapshot=UniverseOptimizationConfiguration(**db_model.configuration_snapshot),
                optimization_metrics=OptimizationMetrics(**db_model.optimization_metrics),
                symbol_fingerprints=db_model.symbol_fingerprints
            )

class InMemoryOptimizationRepository(IUniverseOptimizationRepository):
    """
    In-memory implementation for testing.
    """
    def __init__(self):
        self._store = {}
        
    async def save_optimized_universe(self, universe: OptimizedUniverse) -> None:
        self._store[universe.optimized_universe_id] = universe
        
    async def load_optimized_universe(self, optimized_universe_id: str) -> OptimizedUniverse:
        if optimized_universe_id not in self._store:
            raise ValueError("Not found")
        return self._store[optimized_universe_id]
