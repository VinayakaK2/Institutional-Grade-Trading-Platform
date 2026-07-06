"""
Cache Manager
High-level abstraction for interacting with caching mechanisms.
"""
from typing import Any, Optional, TypeVar
from backend.infrastructure.cache.provider import CacheProvider
from backend.infrastructure.cache.keys import CacheKeyBuilder
from backend.infrastructure.redis.cache import CacheService as RedisProvider # Using Phase 1.2 Redis as default
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

class CacheManager:
    """Manages cache operations by delegating to a configured provider."""
    
    def __init__(self, provider: Optional[CacheProvider] = None):
        # Default to Phase 1.2 Redis CacheService if not explicitly provided
        self._provider = provider or RedisProvider()

    async def get(self, namespace: str, entity: str, identifier: str) -> Optional[Any]:
        key = CacheKeyBuilder.build(namespace, entity, identifier)
        logger.debug(f"Cache miss/hit check for key: {key}")
        return await self._provider.get(key)

    async def set(self, namespace: str, entity: str, identifier: str, value: Any, ttl: int = 3600) -> None:
        key = CacheKeyBuilder.build(namespace, entity, identifier)
        logger.debug(f"Setting cache for key: {key} with TTL: {ttl}s")
        await self._provider.set(key, value, ttl_seconds=ttl)

    async def delete(self, namespace: str, entity: str, identifier: str) -> None:
        key = CacheKeyBuilder.build(namespace, entity, identifier)
        logger.debug(f"Deleting cache for key: {key}")
        await self._provider.delete(key)
