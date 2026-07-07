from sqlalchemy import Column, String, Integer, DateTime, JSON
from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.mixins import TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any, List

class UniverseSnapshotModel(Base, TimestampMixin):
    """
    SQLAlchemy mapping for UniverseSnapshot.
    Persists the immutable snapshots of the universe pipeline.
    """
    __tablename__ = 'universe_snapshots'

    snapshot_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # created_at is provided by TimestampMixin
    
    symbol_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Store serialized UniverseInstrument objects as JSON
    instruments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    metadata_col: Mapped[Dict[str, Any]] = mapped_column('metadata', JSON, nullable=False)
    
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(50), nullable=False)
