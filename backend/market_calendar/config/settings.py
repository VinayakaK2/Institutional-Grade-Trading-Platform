"""
Market Calendar Settings
"""
from pydantic import Field
from backend.infrastructure.config.settings import AppSettings

class MarketCalendarSettings(AppSettings):
    """Configuration for Market Calendars."""
    primary_provider: str = Field(default="static_calendar", description="Primary calendar data source")
    default_exchange: str = Field(default="NSE", description="Default exchange if not specified")
    cache_ttl_seconds: int = Field(default=86400, description="Cache TTL for calendar data (default 24h)")

market_calendar_settings = MarketCalendarSettings()
