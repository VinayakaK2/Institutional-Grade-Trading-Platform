import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.infrastructure.database.orm.base import Base
from backend.universe_engine.classification.repository import PostgresClassificationRepository

@pytest_asyncio.fixture
async def async_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, expire_on_commit=False)

@pytest_asyncio.fixture
async def postgres_repo(async_session_factory):
    return PostgresClassificationRepository(async_session_factory)

@pytest.mark.asyncio
async def test_postgres_repository_save_and_load(postgres_repo, test_engine, mock_classification_provider, parent_certified_universe, parent_liquidity_metrics):
    mock_classification_provider.sectors["AAPL"] = "Technology"
    mock_classification_provider.industries["AAPL"] = "Consumer Electronics"
    mock_classification_provider.market_caps["AAPL"] = 3_000_000_000_000.0 

    result = await test_engine.generate_classified_universe(
        run_id="test_run",
        parent_certified_universe=parent_certified_universe,
        parent_liquidity_metrics=parent_liquidity_metrics
    )

    universe = result.universe

    # Save to postgres
    await postgres_repo.save_classified_universe(universe)

    # Load from postgres
    loaded = await postgres_repo.load_classified_universe(universe.classified_universe_id)
    
    assert loaded is not None
    assert loaded.classified_universe_id == universe.classified_universe_id
    assert loaded.parent_certified_universe_id == universe.parent_certified_universe_id
    assert loaded.pipeline_version == universe.pipeline_version
    assert loaded.config_hash == universe.config_hash
    assert len(loaded.classified_symbols) == 2
    assert loaded.statistics.total_symbols == 2
    
    # Check if loaded AAPL values match
    aapl = next(s for s in loaded.classified_symbols if s.symbol.symbol.symbol == "AAPL")
    assert aapl.sector == "Technology"
    assert aapl.industry == "Consumer Electronics"

@pytest.mark.asyncio
async def test_postgres_repository_load_not_found(postgres_repo):
    loaded = await postgres_repo.load_classified_universe("non_existent")
    assert loaded is None
