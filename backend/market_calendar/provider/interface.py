"""
Market Calendar Provider Interface
"""
from typing import Protocol
from datetime import date
from backend.market_calendar.models.session import DailySchedule

class BaseCalendarProvider(Protocol):
    """
    Abstract protocol for calendar providers (e.g. static memory, API-based).
    """
    @property
    def name(self) -> str:
        """Unique identifier for the calendar provider."""
        ...
        
    @property
    def is_healthy(self) -> bool:
        """Returns True if the provider is available."""
        ...

    def get_exchange_timezone(self, exchange_code: str) -> str:
        """Returns the IANA timezone string for the exchange (e.g., 'America/New_York')."""
        ...

    async def get_daily_schedule(self, exchange_code: str, target_date: date) -> DailySchedule:
        """Retrieves the complete session schedule for a given local date at the exchange."""
        ...
