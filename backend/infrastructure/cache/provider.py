"""
Cache Provider Interface
"""
from typing import Protocol, Any, Optional

class CacheProvider(Protocol):
    """Abstract interface for a cache backend."""
    
    async def get(self, key: str) -> Optional[Any]:
        ...
        
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        ...
        
    async def delete(self, key: str) -> None:
        ...
