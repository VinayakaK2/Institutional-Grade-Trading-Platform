"""
Integration Tests for Caching Framework
"""
import pytest
from typing import Any
from backend.infrastructure.cache.manager import CacheManager
from backend.infrastructure.cache.keys import CacheKeyBuilder

# Mock provider for testing without live Redis
class MockCacheProvider:
    def __init__(self):
        self.store = {}
        
    async def get(self, key: str):
        return self.store.get(key)
        
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        self.store[key] = value
        
    async def delete(self, key: str):
        self.store.pop(key, None)

@pytest.mark.asyncio
async def test_cache_manager():
    provider = MockCacheProvider()
    manager = CacheManager(provider=provider)
    
    await manager.set("test_namespace", "user", "123", {"name": "Test"})
    
    val = await manager.get("test_namespace", "user", "123")
    assert val == {"name": "Test"}
    
    await manager.delete("test_namespace", "user", "123")
    val_after = await manager.get("test_namespace", "user", "123")
    assert val_after is None

def test_cache_key_builder():
    key = CacheKeyBuilder.build("app", "User", "123")
    assert key == "app:user:123"
