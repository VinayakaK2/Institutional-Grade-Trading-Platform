import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from backend.infrastructure.database.orm.base import Base

@pytest_asyncio.fixture(scope="session")
def engine():
    """Create an in-memory SQLite engine for tests."""
    # StaticPool keeps the same connection for the life of the engine in SQLite
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False
    )

@pytest_asyncio.fixture(scope="function")
async def setup_database(engine):
    """Create all tables before each test and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(engine, setup_database):
    """Provide a database session for tests."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
