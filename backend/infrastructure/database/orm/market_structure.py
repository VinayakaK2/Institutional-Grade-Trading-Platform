from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.infrastructure.database.orm.base import Base

class MarketStructurePointModel(Base):
    """
    SQLAlchemy Model for MarketStructurePoint (HH, HL, LH, LL).
    """
    __tablename__ = "market_structure_points"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    structure_type: Mapped[str] = mapped_column(String(10), nullable=False) # HH, HL, LH, LL
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Complete SwingPoint as JSON
    swing_point: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Complete SymbolReference as JSON
    symbol_reference: Mapped[dict] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_ms_points_sym_tf_ds", "symbol", "timeframe", "dataset_version"),
        Index("ix_ms_points_sym_tf_ts", "symbol", "timeframe", "timestamp"),
    )

class MarketStructureEventModel(Base):
    """
    SQLAlchemy Model for StructureEvent (BOS, CHOCH).
    """
    __tablename__ = "market_structure_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    event_type: Mapped[str] = mapped_column(String(10), nullable=False) # BOS, CHOCH
    event_signal: Mapped[str] = mapped_column(String(20), nullable=False) # BULLISH, BEARISH
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Trigger candle as JSON
    trigger_candle: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Broken reference swing as JSON
    reference_swing: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Complete SymbolReference as JSON
    symbol_reference: Mapped[dict] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_ms_events_sym_tf_ds", "symbol", "timeframe", "dataset_version"),
        Index("ix_ms_events_sym_tf_ts", "symbol", "timeframe", "timestamp"),
    )
