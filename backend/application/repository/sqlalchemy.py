"""
SQLAlchemy Generic Repository
"""
from typing import TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc

from backend.application.repository.base import BaseRepository
from backend.domain.shared.primitives import PaginationRequest, PaginationResponse, SortDirection
from backend.infrastructure.database.orm.base import Base

T = TypeVar("T", bound=Base)

class SqlAlchemyRepository(BaseRepository[T]):
    """
    Concrete SQLAlchemy implementation of the generic repository.
    """
    
    def __init__(self, model_class: Type[T], session: AsyncSession):
        self._model_class = model_class
        self._session = session

    async def get_by_id(self, id: Any) -> Optional[T]:
        return await self._session.get(self._model_class, id)
        
    async def get_all(self) -> List[T]:
        result = await self._session.execute(select(self._model_class))
        return list(result.scalars().all())
        
    async def get_paginated(self, request: PaginationRequest) -> PaginationResponse[T]:
        query = select(self._model_class)
        
        # Sorting
        if request.sort:
            for sort_opt in request.sort:
                column = getattr(self._model_class, sort_opt.field, None)
                if column is not None:
                    if sort_opt.direction == SortDirection.DESC:
                        query = query.order_by(desc(column))
                    else:
                        query = query.order_by(asc(column))
        
        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self._session.scalar(count_query) or 0
        
        # Pagination
        query = query.offset(request.offset).limit(request.page_size)
        result = await self._session.execute(query)
        items = list(result.scalars().all())
        
        return PaginationResponse(
            items=items,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size
        )
        
    async def add(self, entity: T) -> T:
        self._session.add(entity)
        return entity
        
    async def update(self, entity: T) -> T:
        # With SQLAlchemy, if it's attached to the session, modifications are tracked.
        # But we can explicitly merge to be safe.
        merged = await self._session.merge(entity)
        return merged
        
    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        
    async def add_bulk(self, entities: List[T]) -> None:
        self._session.add_all(entities)
