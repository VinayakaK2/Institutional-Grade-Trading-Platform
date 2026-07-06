"""
Database Manager
Handles the lifecycle of the database infrastructure (startup, shutdown, health check).
"""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from backend.infrastructure.database.session import engine
from backend.infrastructure.database.exceptions import DatabaseConnectionException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Manages the database lifecycle and global state."""
    
    @staticmethod
    async def startup() -> None:
        """Initializes the database connection and verifies viability."""
        logger.info("Initializing database connection...")
        try:
            await DatabaseManager.ping()
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.critical("Failed to connect to the database on startup.", exc_info=True)
            raise DatabaseConnectionException(
                message="Critical failure: Could not establish database connection during startup.",
                details={"error": str(e)}
            ) from e

    @staticmethod
    async def shutdown() -> None:
        """Safely disposes the database engine pool."""
        logger.info("Disposing database connection pool...")
        try:
            await engine.dispose()
            logger.info("Database connection pool disposed.")
        except Exception:
            logger.error("Error disposing database engine.", exc_info=True)

    @staticmethod
    async def ping() -> bool:
        """
        Executes a lightweight query to verify the database is accessible.
        Used by the Observability Foundation's readiness check.
        """
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error("Database health check ping failed.", details={"error": str(e)})
            raise DatabaseConnectionException(
                message="Database health check failed.",
                details={"error": str(e)}
            ) from e
