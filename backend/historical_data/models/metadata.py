"""
Historical Data Models - Metadata
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference

class DownloadStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class DownloadRequest(BaseModel):
    """Encapsulates a request for historical data."""
    symbol: SymbolReference
    timeframe: Timeframe
    start_date: datetime
    end_date: datetime
    provider: Optional[str] = None
    priority: int = 1

class DownloadMetadata(BaseModel):
    """Tracks the state and metadata of a historical download."""
    request_id: str
    symbol: SymbolReference
    timeframe: Timeframe
    provider: str
    status: DownloadStatus = DownloadStatus.PENDING
    start_date: datetime
    end_date: datetime
    
    last_successful_sync: Optional[datetime] = None
    retry_count: int = 0
    failure_reason: Optional[str] = None
    download_duration_ms: Optional[int] = None
    
    records_downloaded: int = 0
    records_saved: int = 0
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
