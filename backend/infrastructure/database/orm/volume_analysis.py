from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.database.orm.base import Base

class VolumeAnalysisModel(Base):
    """
    SQLAlchemy Model for VolumeAnalysisResult.
    """
    __tablename__ = "volume_analysis_results"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    avg_volume: Mapped[float] = mapped_column(Float, nullable=False)
    rvol: Mapped[float] = mapped_column(Float, nullable=False)
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Complete SymbolReference as JSON
    symbol_reference: Mapped[dict] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_vol_analysis_sym_tf_ds", "symbol", "timeframe", "dataset_version"),
        Index("ix_vol_analysis_sym_tf_ts", "symbol", "timeframe", "timestamp"),
    )

class VolumeEventModel(Base):
    """
    SQLAlchemy Model for VolumeEvent.
    """
    __tablename__ = "volume_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    event_strength: Mapped[float] = mapped_column(Float, nullable=False)
    relative_volume: Mapped[float] = mapped_column(Float, nullable=False)
    candle_classification: Mapped[str] = mapped_column(String(20), nullable=False)
    
    trigger_candle: Mapped[dict] = mapped_column(JSON, nullable=False)
    symbol_reference: Mapped[dict] = mapped_column(JSON, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_vol_events_sym_tf_ds", "symbol", "timeframe", "dataset_version"),
        Index("ix_vol_events_sym_tf_ts", "symbol", "timeframe", "timestamp"),
    )
