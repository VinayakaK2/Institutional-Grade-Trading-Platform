from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.database.orm.base import Base

class SupportResistanceZoneModel(Base):
    __tablename__ = "support_resistance_zones"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    zone_type: Mapped[str] = mapped_column(String(20), nullable=False)
    center: Mapped[float] = mapped_column(Float, nullable=False)
    upper_boundary: Mapped[float] = mapped_column(Float, nullable=False)
    lower_boundary: Mapped[float] = mapped_column(Float, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Store source swing point as JSON for flexibility
    source_swing_point: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Store complete SymbolReference as JSON
    symbol_reference: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Store strength metrics as JSON
    strength: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_sr_zones_sym_tf_ds_active", "symbol", "timeframe", "dataset_version", "is_active"),
        Index("ix_sr_zones_sym_tf_created", "symbol", "timeframe", "created_at"),
    )
