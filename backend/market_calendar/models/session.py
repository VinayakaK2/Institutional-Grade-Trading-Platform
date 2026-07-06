"""
Trading Session Models
"""
from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from datetime import time

class SessionType(str, Enum):
    """Types of trading sessions."""
    PRE_MARKET = "PRE_MARKET"
    NORMAL = "NORMAL"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"
    HOLIDAY = "HOLIDAY"
    HALF_DAY = "HALF_DAY"

class SessionSchedule(BaseModel):
    """Defines the schedule for a specific session type."""
    session_type: SessionType
    start_local_time: time
    end_local_time: time

class DailySchedule(BaseModel):
    """The complete schedule for a given trading day at an exchange."""
    exchange_code: str
    date_str: str = Field(..., description="YYYY-MM-DD")
    is_trading_day: bool
    sessions: List[SessionSchedule] = Field(default_factory=list)
