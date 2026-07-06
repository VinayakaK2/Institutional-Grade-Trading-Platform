"""
Retry Policy
Implements exponential backoff with jitter for resilient async operations.
"""
import asyncio
import random
from functools import wraps
from typing import Callable, Any, Tuple, TypeVar, Type
from backend.core.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T")

def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff and jitter.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt > max_retries:
                        logger.error(f"Retry limit reached ({max_retries}) for {func.__name__}", exc_info=True)
                        raise
                        
                    # Calculate exponential backoff with jitter
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    jitter = delay * 0.1 * random.uniform(-1, 1)  # nosec B311
                    sleep_time = delay + jitter
                    
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}. Retrying in {sleep_time:.2f}s. Error: {str(e)}")
                    await asyncio.sleep(sleep_time)
        return wrapper
    return decorator
