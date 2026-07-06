"""
Generic Repository Interface
"""
from typing import Protocol, TypeVar, List, Optional, Any
from backend.domain.shared.primitives import PaginationRequest, PaginationResponse

T = TypeVar("T")

class BaseRepository(Protocol[T]):
    """
    Abstract generic repository protocol for all domain entities.
    """
    
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Retrieves an entity by its identifier."""
        ...
        
    async def get_all(self) -> List[T]:
        """Retrieves all entities."""
        ...
        
    async def get_paginated(self, request: PaginationRequest) -> PaginationResponse[T]:
        """Retrieves a paginated list of entities."""
        ...
        
    async def add(self, entity: T) -> T:
        """Adds a new entity."""
        ...
        
    async def update(self, entity: T) -> T:
        """Updates an existing entity."""
        ...
        
    async def delete(self, entity: T) -> None:
        """Deletes an entity."""
        ...
        
    async def add_bulk(self, entities: List[T]) -> None:
        """Adds multiple entities efficiently."""
        ...
