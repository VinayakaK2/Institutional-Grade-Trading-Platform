"""
Connection Utilities
Helper functions for managing retry policies and connection resilience.
"""
import asyncio
from typing import Callable, Any, TypeVar, Coroutine
from functools import wraps
from sqlalchemy.exc import OperationalError

from backend.infrastructure.database.exceptions import DatabaseConnectionException
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

def with_retry(max_retries: int = 3, base_delay: float = 1.0) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """
    A decorator that retries a database operation upon OperationalError (e.g., connection drops).
    Uses exponential backoff.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Database operation failed after {max_retries} retries.", exc_info=True)
                        raise DatabaseConnectionException(
                            message=f"Database connection failed after {max_retries} retries.",
                            details={"error": str(e)}
                        ) from e
                    
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(f"Database connection error. Retrying {retries}/{max_retries} in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
