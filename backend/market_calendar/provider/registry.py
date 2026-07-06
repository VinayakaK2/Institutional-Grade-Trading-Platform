"""
Calendar Provider Registry
"""
from typing import Dict, Optional
from backend.market_calendar.provider.interface import BaseCalendarProvider
from backend.core.logger import get_logger

logger = get_logger(__name__)

class CalendarProviderRegistry:
    """Registry for all market calendar providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseCalendarProvider] = {}
        
    def register(self, provider: BaseCalendarProvider) -> None:
        self._providers[provider.name] = provider
        logger.debug(f"Registered Market Calendar Provider: {provider.name}")
        
    def get(self, name: str) -> Optional[BaseCalendarProvider]:
        return self._providers.get(name)

calendar_provider_registry = CalendarProviderRegistry()
