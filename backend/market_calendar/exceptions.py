"""
Market Calendar Exceptions
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class MarketCalendarException(InfrastructureException):
    """Base exception for all market calendar errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "MARKET_CALENDAR_ERROR"

class MissingCalendarDataException(MarketCalendarException):
    """Raised when calendar data is unavailable for a given exchange or date."""
    def __init__(self, exchange: str, date_str: str, message: str = "Missing calendar data.") -> None:
        super().__init__(message=message, details={"exchange": exchange, "date": date_str})
        self.error_code = "MISSING_CALENDAR_DATA"

class InvalidTimezoneException(MarketCalendarException):
    """Raised when an invalid timezone string is provided."""
    def __init__(self, timezone: str, message: str = "Invalid timezone provided.") -> None:
        super().__init__(message=message, details={"timezone": timezone})
        self.error_code = "INVALID_TIMEZONE"

class ProviderOfflineException(MarketCalendarException):
    """Raised when the calendar provider fails."""
    def __init__(self, provider_name: str, message: str = "Calendar provider offline.") -> None:
        super().__init__(message=message, details={"provider": provider_name})
        self.error_code = "CALENDAR_PROVIDER_OFFLINE"
