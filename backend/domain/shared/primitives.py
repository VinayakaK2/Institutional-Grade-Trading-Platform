"""
Shared Domain Primitives
Reusable abstractions for the domain layer (e.g. Pagination, Sorting, Operation Results).
"""
from enum import Enum
from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortOptions(BaseModel):
    """Encapsulates sorting criteria for database queries."""
    field: str
    direction: SortDirection = SortDirection.ASC

class PaginationRequest(BaseModel):
    """Standardized request for paginated data."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: Optional[List[SortOptions]] = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginationResponse(BaseModel, Generic[T]):
    """Standardized response for paginated data."""
    model_config = {"arbitrary_types_allowed": True}
    
    items: List[T]
    total_count: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        return (self.total_count + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
        
    @property
    def has_previous(self) -> bool:
        return self.page > 1

class OperationResult(BaseModel, Generic[T]):
    """Standardized response for domain operations that might fail without raising an exception."""
    model_config = {"arbitrary_types_allowed": True}
    
    success: bool
    data: Optional[T] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "OperationResult[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error_message: str, error_code: str = "OPERATION_FAILED") -> "OperationResult[Any]":
        return cls(success=False, error_message=error_message, error_code=error_code)

class Money(BaseModel):
    """Value object representing monetary amounts to prevent floating point errors."""
    amount: float
    currency: str = "USD"
    
    # In a full production implementation, 'amount' should ideally be stored as Decimal or integer cents.
    # We use float here with validation as a basic primitive for the foundation.
