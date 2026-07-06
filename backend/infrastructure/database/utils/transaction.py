"""
Transaction Utilities
Provides helper decorators and context managers to ensure safe transaction boundaries,
wrapping SQLAlchemy exceptions into our internal Exception hierarchy.
"""
from typing import Callable, Any, TypeVar, Coroutine, Optional
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from backend.infrastructure.database.session import async_session_factory
from backend.infrastructure.database.exceptions import DatabaseTransactionException, DatabaseIntegrityException
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

def transactional(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    A decorator that wraps an async function in a database transaction.
    Injects the session as a kwarg if not provided.
    Rolls back on any exception and translates SQLAlchemy exceptions.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        # Check if session is already provided by the caller
        session: Optional[AsyncSession] = kwargs.get("session")
        owns_session = False
        
        if not session:
            session = async_session_factory()
            kwargs["session"] = session
            owns_session = True
            
        try:
            result = await func(*args, **kwargs)
            if owns_session:
                await session.commit()
            return result
        except IntegrityError as e:
            if owns_session:
                await session.rollback()
            logger.warning("Database integrity error during transaction.", exc_info=True)
            raise DatabaseIntegrityException(
                message="Data integrity constraint violated.",
                details={"error": str(e.orig)}
            ) from e
        except SQLAlchemyError as e:
            if owns_session:
                await session.rollback()
            logger.error("Database transaction error.", exc_info=True)
            raise DatabaseTransactionException(
                message="An error occurred during a database transaction.",
                details={"error": str(e)}
            ) from e
        except Exception:
            # For non-DB exceptions, still rollback
            if owns_session:
                await session.rollback()
            raise
        finally:
            if owns_session:
                await session.close()
                
    return wrapper
