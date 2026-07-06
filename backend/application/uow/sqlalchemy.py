"""
SQLAlchemy Unit of Work
"""
from typing import Any, Dict, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from backend.application.uow.base import BaseUnitOfWork
from backend.application.repository.base import BaseRepository
from backend.application.repository.sqlalchemy import SqlAlchemyRepository
from backend.infrastructure.database.session import async_session_factory
from backend.infrastructure.database.exceptions import DatabaseTransactionException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class SqlAlchemyUnitOfWork(BaseUnitOfWork):
    """
    Concrete Unit of Work for SQLAlchemy.
    Manages session lifecycle and coordinates repositories.
    """
    
    def __init__(self, session_factory: Any = async_session_factory):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._repositories: Dict[Type, BaseRepository] = {}

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                # Exception occurred inside the context block, rollback.
                await self.rollback()
            else:
                # In standard UoW, explicit commit is usually required by the caller.
                # However, if we want auto-commit: await self.commit()
                pass 
        finally:
            if self._session:
                await self._session.close()
                self._session = None

    async def commit(self) -> None:
        if not self._session:
            raise DatabaseTransactionException("Cannot commit outside of a transaction context.")
        try:
            await self._session.commit()
        except SQLAlchemyError as e:
            await self.rollback()
            logger.error("Unit of Work commit failed.", exc_info=True)
            raise DatabaseTransactionException("Transaction commit failed.", {"error": str(e)}) from e

    async def rollback(self) -> None:
        if self._session:
            try:
                await self._session.rollback()
            except SQLAlchemyError:
                logger.error("Unit of Work rollback failed.", exc_info=True)

    def repository(self, model_class: type) -> BaseRepository:
        if not self._session:
            raise DatabaseTransactionException("Cannot access repository outside of a transaction context.")
            
        if model_class not in self._repositories:
            self._repositories[model_class] = SqlAlchemyRepository(model_class, self._session)
            
        return self._repositories[model_class]
