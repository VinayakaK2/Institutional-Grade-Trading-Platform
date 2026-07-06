"""
ORM Mixins
Reusable behaviors for database entities.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Provides created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=_utc_now, 
        nullable=False,
        comment="When the record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=_utc_now, 
        onupdate=_utc_now, 
        nullable=False,
        comment="When the record was last updated"
    )


class SoftDeleteMixin:
    """Provides soft delete capabilities."""
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True,
        comment="True if the record is logically deleted"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="When the record was logically deleted"
    )
    
    def soft_delete(self) -> None:
        """Marks the record as deleted."""
        self.is_deleted = True
        self.deleted_at = _utc_now()


class AuditMixin:
    """Provides audit trails and optimistic locking."""
    # created_by and updated_by store user IDs or service names
    created_by: Mapped[Optional[str]] = mapped_column(
        String, 
        nullable=True,
        comment="Identity that created the record"
    )
    
    updated_by: Mapped[Optional[str]] = mapped_column(
        String, 
        nullable=True,
        comment="Identity that last updated the record"
    )
    
    # Version field for Optimistic Locking
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Version number for optimistic concurrency control"
    )
    
    __mapper_args__ = {
        "version_id_col": version
    }
