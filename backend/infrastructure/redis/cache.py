"""
Cache Abstraction
Provides a clean interface for interacting with Redis as a cache.
Includes automatic key prefixing and fallback TTL handling.
"""
from typing import Optional
from redis.exceptions import RedisError

from backend.infrastructure.redis.client import get_redis_client
from backend.infrastructure.redis.config import redis_settings
from backend.infrastructure.redis.exceptions import RedisOperationException
from backend.infrastructure.utils.serialization import SerializationHelper
from backend.core.logger import get_logger

logger = get_logger(__name__)

class CacheService:
    """Abstracts common Redis cache operations."""
    
    def __init__(self):
        self.client = get_redis_client()
        self.prefix = redis_settings.redis_key_prefix
        self.default_ttl = redis_settings.redis_default_ttl

    def _build_key(self, key: str) -> str:
        """Appends the global namespace prefix."""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[dict]:
        """Retrieves and deserializes a JSON payload from the cache."""
        full_key = self._build_key(key)
        try:
            data = await self.client.get(full_key)
            if data is None:
                return None
            return SerializationHelper.deserialize_dict(data)
        except RedisError as e:
            logger.error(f"Failed to GET key {full_key} from cache.", exc_info=True)
            raise RedisOperationException("Cache GET operation failed.", {"key": full_key, "error": str(e)}) from e

    async def set(self, key: str, value: dict, ttl_seconds: Optional[int] = None) -> None:
        """Serializes and stores a payload in the cache."""
        full_key = self._build_key(key)
        expire_time = ttl_seconds if ttl_seconds is not None else self.default_ttl
        try:
            serialized_data = SerializationHelper.serialize_dict(value)
            await self.client.setex(name=full_key, time=expire_time, value=serialized_data)
        except RedisError as e:
            logger.error(f"Failed to SET key {full_key} in cache.", exc_info=True)
            raise RedisOperationException("Cache SET operation failed.", {"key": full_key, "error": str(e)}) from e

    async def delete(self, key: str) -> None:
        """Removes a key from the cache."""
        full_key = self._build_key(key)
        try:
            await self.client.delete(full_key)
        except RedisError as e:
            logger.error(f"Failed to DELETE key {full_key} from cache.", exc_info=True)
            raise RedisOperationException("Cache DELETE operation failed.", {"key": full_key, "error": str(e)}) from e
