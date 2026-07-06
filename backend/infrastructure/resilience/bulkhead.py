"""
Bulkhead Pattern
Isolates failures by limiting concurrent executions of a particular block of code.
"""
import asyncio
from typing import Callable, Any, TypeVar
from functools import wraps
from backend.core.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T")

class BulkheadRejectedException(Exception):
    """Raised when the bulkhead is full."""
    pass

class Bulkhead:
    def __init__(self, max_concurrent: int):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
    async def __aenter__(self):
        if self._semaphore.locked():
            raise BulkheadRejectedException("Bulkhead limit reached. Execution rejected.")
        await self._semaphore.acquire()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._semaphore.release()

def with_bulkhead(bulkhead: Bulkhead) -> Callable:
    """Decorator to wrap async function with a bulkhead limit."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with bulkhead:
                return await func(*args, **kwargs)
        return wrapper
    return decorator
