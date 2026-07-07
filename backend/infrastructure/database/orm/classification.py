from sqlalchemy import Column, String, JSON
from backend.infrastructure.database.orm.base import Base
from backend.infrastructure.database.orm.mixins import TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any, List

class ClassifiedUniverseModel(Base, TimestampMixin):
    """
    SQLAlchemy mapping for ClassifiedUniverse.
    Persists the immutable snapshots of the classification pipeline.
    """
    __tablename__ = 'classified_universes'

    classified_universe_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    parent_certified_universe_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # created_at is provided by TimestampMixin
    
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    config_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    
    classified_symbols: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    configuration_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    statistics: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
