from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from backend.infrastructure.database.orm.base import Base

class OptimizedUniverseModel(Base):
    __tablename__ = "optimized_universes"

    optimized_universe_id = Column(String(36), primary_key=True)
    parent_classified_universe_id = Column(String(36), ForeignKey("classified_universes.classified_universe_id"), nullable=False, index=True)
    previous_optimized_universe_id = Column(String(36), nullable=True)
    pipeline_version = Column(String(50), nullable=False)
    config_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    
    # Store configuration and metrics as JSONB
    configuration_snapshot = Column(JSON, nullable=False)
    optimization_metrics = Column(JSON, nullable=False)
    symbol_fingerprints = Column(JSON, nullable=False)
