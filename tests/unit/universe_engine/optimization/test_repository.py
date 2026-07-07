import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.classification import ClassifiedUniverseModel
from backend.universe_engine.optimization.repository import PostgresOptimizationRepository
from backend.universe_engine.optimization.models import (
    OptimizedUniverse,
    OptimizationMetrics,
    UniverseOptimizationConfiguration
)
from datetime import datetime, timezone
from unittest.mock import patch

@pytest_asyncio.fixture
async def async_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_postgres_optimization_repository(async_session_factory):
    repo = PostgresOptimizationRepository(async_session_factory)
    
    # We need to mock the parent ClassifiedUniverse to satisfy the foreign key constraint.
    # For SQLite in memory, foreign keys might not be strictly enforced by default, 
    # but to be safe, we'll just test saving/loading. SQLite often allows it if PRAGMA foreign_keys is off.
    
    universe = OptimizedUniverse(
        optimized_universe_id="opt1",
        parent_classified_universe_id="parent1",
        previous_optimized_universe_id=None,
        pipeline_version="1.0.0",
        config_hash="hash1",
        created_at=datetime.now(timezone.utc),
        configuration_snapshot=UniverseOptimizationConfiguration(),
        optimization_metrics=OptimizationMetrics(total_symbols=5),
        symbol_fingerprints={"AAPL": "fp1"}
    )
    
    await repo.save_optimized_universe(universe)
    
    loaded = await repo.load_optimized_universe("opt1")
    assert loaded.optimized_universe_id == "opt1"
    assert loaded.parent_classified_universe_id == "parent1"
    assert loaded.optimization_metrics.total_symbols == 5
    assert loaded.symbol_fingerprints["AAPL"] == "fp1"
    
    with pytest.raises(ValueError, match="OptimizedUniverse bad_id not found"):
        await repo.load_optimized_universe("bad_id")
