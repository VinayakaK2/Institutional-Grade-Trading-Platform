"""
Shared ORM Models for Market Data persistence
"""
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import String, Float, DateTime, Boolean, UniqueConstraint, JSON
from datetime import datetime

from backend.infrastructure.database.orm.models import AuditableModel

class RawCandleOrm(AuditableModel):
    """
    SQLAlchemy mapping for RawCandle.
    Stores the exact footprint of what was downloaded before normalization.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "raw_candles"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Store raw as string to avoid any parsing/precision loss from the provider
    raw_timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_open: Mapped[float] = mapped_column(Float, nullable=False)
    raw_high: Mapped[float] = mapped_column(Float, nullable=False)
    raw_low: Mapped[float] = mapped_column(Float, nullable=False)
    raw_close: Mapped[float] = mapped_column(Float, nullable=False)
    raw_volume: Mapped[float] = mapped_column(Float, nullable=False)
    
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint('provider', 'symbol_id', 'timeframe', 'raw_timestamp', name='uix_raw_candle_provider_symbol_tf_ts'),
    )

class QuarantinedCandleOrm(AuditableModel):
    """
    SQLAlchemy mapping for Quarantined Records.
    Stores invalid raw footprints for audit and debug.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "quarantined_candles"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    raw_timestamp: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_open: Mapped[float] = mapped_column(Float, nullable=False)
    raw_high: Mapped[float] = mapped_column(Float, nullable=False)
    raw_low: Mapped[float] = mapped_column(Float, nullable=False)
    raw_close: Mapped[float] = mapped_column(Float, nullable=False)
    raw_volume: Mapped[float] = mapped_column(Float, nullable=False)
    
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    quarantine_reason: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (
        UniqueConstraint('provider', 'symbol_id', 'timeframe', 'raw_timestamp', name='uix_quarantined_candle_provider_symbol_tf_ts'),
    )

class CandleOrm(AuditableModel):
    """
    SQLAlchemy mapping for the canonical normalized Candle.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "canonical_candles"

    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('symbol_id', 'timeframe', 'timestamp', name='uix_canonical_candle_symbol_tf_ts'),
    )

class AdjustedCandleOrm(AuditableModel):
    """
    SQLAlchemy mapping for adjusted historical Candles.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "adjusted_candles"

    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # The dataset_version this candle belongs to
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('dataset_version', 'symbol_id', 'timeframe', 'timestamp', name='uix_adjusted_candle_version_symbol_tf_ts'),
    )
