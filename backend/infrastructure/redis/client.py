"""
Redis Client Foundation
Provides the asynchronous Redis client and connection pool.
"""
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from backend.infrastructure.redis.config import redis_settings

# Global Connection Pool
redis_pool = ConnectionPool.from_url(
    redis_settings.redis_url,
    max_connections=redis_settings.redis_max_connections,
    socket_timeout=redis_settings.redis_timeout,
    retry_on_timeout=redis_settings.redis_retry_on_timeout,
    decode_responses=True # Ensure we get strings back instead of bytes
)

def get_redis_client() -> redis.Redis:
    """
    Returns an async Redis client bound to the global connection pool.
    This client is safe to be shared across async tasks.
    """
    return redis.Redis(connection_pool=redis_pool)
