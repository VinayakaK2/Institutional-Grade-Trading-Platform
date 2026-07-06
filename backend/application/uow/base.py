"""
Unit of Work Protocol
"""
from typing import Protocol, Any
from backend.application.repository.base import BaseRepository

class BaseUnitOfWork(Protocol):
    """
    Abstract Unit of Work protocol for managing transaction boundaries.
    """
    
    async def __aenter__(self) -> "BaseUnitOfWork":
        ...
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...
        
    async def commit(self) -> None:
        """Commits the current transaction."""
        ...
        
    async def rollback(self) -> None:
        """Rolls back the current transaction."""
        ...
        
    def repository(self, model_class: type) -> BaseRepository:
        """Retrieves a repository for a given model."""
        ...
