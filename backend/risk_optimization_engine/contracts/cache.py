from abc import ABC, abstractmethod
from typing import Any, Dict

class ICacheStore(ABC):
    """
    Infrastructure interface for caching risk decision snapshots.
    Cache key must be: BusinessFingerprint hash + Pipeline Version.
    """
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass
        
    @abstractmethod
    async def load(self, key: str) -> Any:
        pass
        
    @abstractmethod
    async def save(self, key: str, snapshot: Any) -> None:
        pass
        
    @abstractmethod
    async def invalidate(self, key: str) -> None:
        pass
        
    @abstractmethod
    async def clear(self) -> None:
        pass
        
    @abstractmethod
    async def stats(self) -> Dict[str, Any]:
        pass
