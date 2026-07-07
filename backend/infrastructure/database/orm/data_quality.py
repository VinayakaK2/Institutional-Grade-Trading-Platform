from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime, timezone

from backend.infrastructure.database.orm.base import Base

class CertifiedUniverseModel(Base):
    __tablename__ = "certified_universes"

    certified_universe_id = Column(String, primary_key=True)
    parent_snapshot_id = Column(String, nullable=False, index=True)
    pipeline_version = Column(String, nullable=False)
    config_hash = Column(String, nullable=False)
    dataset_version = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Store lists of models as JSON to maintain strong typing across the boundary
    certified_symbols = Column(JSON, nullable=False)
    rejected_symbols = Column(JSON, nullable=False)
    
    # Store configuration and stats as JSON
    configuration_snapshot = Column(JSON, nullable=False)
    statistics = Column(JSON, nullable=False)
