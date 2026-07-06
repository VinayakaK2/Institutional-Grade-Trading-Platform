"""
ORM Models for Historical Data Pipeline
"""
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import String, Float, DateTime, Boolean, UniqueConstraint, JSON
from datetime import datetime

from backend.infrastructure.database.orm.models import AuditableModel




class DownloadMetadataOrm(AuditableModel):
    """
    Tracks the state and outcome of historical data download requests.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "download_metadata"
        
    request_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    symbol_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    records_downloaded: Mapped[int] = mapped_column(default=0)
    records_saved: Mapped[int] = mapped_column(default=0)
    
    failure_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    download_duration_ms: Mapped[int] = mapped_column(default=0)
