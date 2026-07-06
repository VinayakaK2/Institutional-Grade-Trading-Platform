"""
Time Utilities
Provides standardized datetime operations to guarantee UTC everywhere.
"""
from datetime import datetime, timezone

class TimeUtils:
    @staticmethod
    def utcnow() -> datetime:
        """Always returns an aware UTC datetime."""
        return datetime.now(timezone.utc)
        
    @staticmethod
    def is_aware(dt: datetime) -> bool:
        """Checks if a datetime has a timezone associated with it."""
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None
