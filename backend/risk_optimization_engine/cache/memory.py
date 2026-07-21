from typing import Any, Dict
import asyncio
import copy
from backend.risk_optimization_engine.contracts.cache import ICacheStore

class MemoryCacheStore(ICacheStore):
    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        
    async def exists(self, key: str) -> bool:
        async with self._lock:
            return key in self._cache
            
    async def load(self, key: str) -> Any:
        async with self._lock:
            val = self._cache.get(key)
            return copy.deepcopy(val) if val is not None else None
            
    async def save(self, key: str, snapshot: Any) -> None:
        async with self._lock:
            self._cache[key] = copy.deepcopy(snapshot)
            
    async def invalidate(self, key: str) -> None:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
            
    async def stats(self) -> Dict[str, Any]:
        async with self._lock:
            return {"size": len(self._cache)}
