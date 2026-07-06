"""
Redis Manager
Handles the lifecycle of the Redis infrastructure.
"""
from redis.exceptions import RedisError

from backend.infrastructure.redis.client import get_redis_client, redis_pool
from backend.infrastructure.redis.exceptions import RedisConnectionException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class RedisManager:
    """Manages the Redis lifecycle and global state."""
    
    @staticmethod
    async def startup() -> None:
        """Initializes the connection and verifies viability via Ping."""
        logger.info("Initializing Redis connection...")
        try:
            await RedisManager.ping()
            logger.info("Redis connection established successfully.")
        except Exception as e:
            logger.critical("Failed to connect to Redis on startup.", exc_info=True)
            raise RedisConnectionException(
                message="Critical failure: Could not establish Redis connection during startup.",
                details={"error": str(e)}
            ) from e

    @staticmethod
    async def shutdown() -> None:
        """Safely disconnects all connections in the pool."""
        logger.info("Disconnecting Redis connection pool...")
        try:
            await redis_pool.disconnect()
            logger.info("Redis connection pool disconnected.")
        except Exception:
            logger.error("Error disconnecting Redis engine.", exc_info=True)

    @staticmethod
    async def ping() -> bool:
        """
        Executes a lightweight PING to verify Redis is accessible.
        Used by the Observability Foundation's readiness check.
        """
        try:
            client = get_redis_client()
            response = await client.ping()
            return response
        except RedisError as e:
            logger.error("Redis health check ping failed.", details={"error": str(e)})
            raise RedisConnectionException(
                message="Redis health check failed.",
                details={"error": str(e)}
            ) from e
