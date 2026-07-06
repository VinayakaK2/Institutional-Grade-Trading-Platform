import pytest
import json
from unittest.mock import AsyncMock, patch
from redis.exceptions import RedisError
from backend.infrastructure.redis.cache import CacheService
from backend.infrastructure.redis.exceptions import RedisOperationException

@pytest.fixture
def mock_redis_client():
    mock = AsyncMock()
    return mock

@pytest.fixture
def cache_service(mock_redis_client):
    with patch("backend.infrastructure.redis.cache.get_redis_client", return_value=mock_redis_client):
        service = CacheService()
        return service

@pytest.mark.asyncio
async def test_cache_get_success(cache_service, mock_redis_client):
    mock_redis_client.get.return_value = json.dumps({"test": "data"}).encode("utf-8")
    result = await cache_service.get("test_key")
    assert result == {"test": "data"}
    mock_redis_client.get.assert_called_once_with("swingbot:test_key")

@pytest.mark.asyncio
async def test_cache_get_not_found(cache_service, mock_redis_client):
    mock_redis_client.get.return_value = None
    result = await cache_service.get("test_key")
    assert result is None

@pytest.mark.asyncio
async def test_cache_get_error(cache_service, mock_redis_client):
    mock_redis_client.get.side_effect = RedisError("Connection Error")
    with pytest.raises(RedisOperationException):
        await cache_service.get("test_key")

@pytest.mark.asyncio
async def test_cache_set_success(cache_service, mock_redis_client):
    await cache_service.set("test_key", {"test": "data"}, ttl_seconds=60)
    mock_redis_client.setex.assert_called_once()
    args, kwargs = mock_redis_client.setex.call_args
    assert kwargs["name"] == "swingbot:test_key"
    assert kwargs["time"] == 60

@pytest.mark.asyncio
async def test_cache_set_error(cache_service, mock_redis_client):
    mock_redis_client.setex.side_effect = RedisError("Connection Error")
    with pytest.raises(RedisOperationException):
        await cache_service.set("test_key", {"test": "data"})

@pytest.mark.asyncio
async def test_cache_delete_success(cache_service, mock_redis_client):
    await cache_service.delete("test_key")
    mock_redis_client.delete.assert_called_once_with("swingbot:test_key")

@pytest.mark.asyncio
async def test_cache_delete_error(cache_service, mock_redis_client):
    mock_redis_client.delete.side_effect = RedisError("Connection Error")
    with pytest.raises(RedisOperationException):
        await cache_service.delete("test_key")
