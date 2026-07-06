"""
Database Session Management
Provides the AsyncEngine and AsyncSession factory for the application.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from backend.infrastructure.database.config import db_settings
from backend.core.logger import get_logger

logger = get_logger(__name__)

def create_engine() -> AsyncEngine:
    """Creates the global SQLAlchemy async engine based on config."""
    url = db_settings.get_database_url()
    
    # SQLite has different pooling requirements (often NullPool for testing to avoid lock issues)
    if "sqlite" in url:
        return create_async_engine(
            url,
            echo=db_settings.db_echo,
            poolclass=NullPool
        )
        
    return create_async_engine(
        url,
        echo=db_settings.db_echo,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=db_settings.db_pool_size,
        max_overflow=db_settings.db_max_overflow,
        pool_timeout=db_settings.db_pool_timeout,
        pool_recycle=db_settings.db_pool_recycle,
    )

# Global engine instance
engine = create_engine()

# Global session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection helper to yield a database session.
    Ensures the session is safely closed after use.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
