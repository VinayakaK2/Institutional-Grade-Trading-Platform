import pytest
import pytest_asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.infrastructure.database.orm.base import Base
# Import all models so Base.metadata.create_all finds them

from backend.universe_engine.liquidity.repository import PostgresLiquidityRepository
from backend.universe_engine.liquidity.models import (
    LiquidityQualifiedUniverse,
    LiquidityFilterConfiguration,
    LiquidityFilterStatistics,
    RejectionDetail,
    LiquidityRejectionReason
)

@pytest_asyncio.fixture
async def db_session_factory():
    # Use in-memory SQLite for repository testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    yield session_factory
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_postgres_liquidity_repository_save_and_load(db_session_factory, create_test_instrument):
    repository = PostgresLiquidityRepository(session_factory=db_session_factory)
    
    instrument_pass = create_test_instrument("PASS_1")
    instrument_fail = create_test_instrument("FAIL_VOL_1")
    
    rejection = RejectionDetail(
        instrument_symbol=instrument_fail.symbol.symbol,
        stage_name="AverageDailyVolumeFilter",
        reason=LiquidityRejectionReason.VOLUME_BELOW_THRESHOLD,
        measured_value="100000.0",
        threshold="500000.0"
    )
    
    universe = LiquidityQualifiedUniverse(
        liquidity_universe_id="lu_test_123",
        parent_snapshot_id="parent_snapshot_456",
        pipeline_version="1.0.0",
        config_hash="abc123hash",
        created_at=datetime.now(timezone.utc),
        qualified_symbols=[instrument_pass],
        rejected_symbols=[rejection],
        configuration_snapshot=LiquidityFilterConfiguration(),
        statistics=LiquidityFilterStatistics(
            initial_instrument_count=2,
            final_qualified_count=1,
            volume_rejections=1
        )
    )
    
    # Save
    await repository.save_liquidity_universe(universe)
    
    # Load
    loaded = await repository.load_liquidity_universe("lu_test_123")
    
    assert loaded is not None
    assert loaded.liquidity_universe_id == "lu_test_123"
    assert loaded.parent_snapshot_id == "parent_snapshot_456"
    assert len(loaded.qualified_symbols) == 1
    assert loaded.qualified_symbols[0].symbol.symbol == "PASS_1"
    
    assert len(loaded.rejected_symbols) == 1
    assert loaded.rejected_symbols[0].instrument_symbol == "FAIL_VOL_1"
    assert loaded.rejected_symbols[0].reason == LiquidityRejectionReason.VOLUME_BELOW_THRESHOLD
    
    assert loaded.statistics.initial_instrument_count == 2
    assert loaded.statistics.volume_rejections == 1
