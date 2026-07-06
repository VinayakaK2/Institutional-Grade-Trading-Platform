"""
Abstract Base Models
Reusable abstract models combining the base metadata with specific mixins.
"""
import uuid
import re
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import String

from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


def camel_to_snake(name: str) -> str:
    """Converts CamelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class BaseModel(Base):
    """
    The standard base model for all entities.
    Provides an auto-generated UUID primary key and snake_case table name generation.
    """
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-generate table name based on class name (pluralized snake_case)."""
        snake_name = camel_to_snake(cls.__name__)
        # Simple pluralization rule. Real implementations might use a library, 
        # but this suffices for the foundation.
        if snake_name.endswith('y'):
            return f"{snake_name[:-1]}ies"
        elif snake_name.endswith('s'):
            return f"{snake_name}es"
        return f"{snake_name}s"

    # We use a String representation of UUID to remain driver-agnostic (SQLite support),
    # but in a PostgreSQL-only setup, PG_UUID is preferred.
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier (UUID4)"
    )


class AuditableModel(BaseModel, TimestampMixin, AuditMixin):
    """
    A model that includes timestamps, audit tracking, and optimistic locking.
    """
    __abstract__ = True


class SoftDeleteModel(BaseModel, TimestampMixin, SoftDeleteMixin):
    """
    A model that supports soft deletion and timestamps.
    """
    __abstract__ = True
