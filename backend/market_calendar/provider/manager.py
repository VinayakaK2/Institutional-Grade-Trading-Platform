"""
Calendar Provider Manager
Coordinates request failover across primary and secondary calendar providers.
"""
from typing import Callable, Coroutine, Any, Optional
from backend.market_calendar.provider.interface import BaseCalendarProvider
from backend.market_calendar.provider.registry import CalendarProviderRegistry, calendar_provider_registry as default_registry
from backend.market_calendar.config.settings import market_calendar_settings
from backend.market_calendar.exceptions import ProviderOfflineException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class CalendarProviderManager:
    """Manages calendar provider selection and failover."""
    
    def __init__(self, registry: Optional[CalendarProviderRegistry] = None):
        self._registry = registry or default_registry
        
    def _get_active_provider(self) -> BaseCalendarProvider:
        """Returns the primary healthy provider. (Calendar logic is critical, usually static)"""
        primary = self._registry.get(market_calendar_settings.primary_provider)
        
        if primary and primary.is_healthy:
            return primary
            
        logger.critical(f"Primary calendar provider '{market_calendar_settings.primary_provider}' is unavailable.")
        raise ProviderOfflineException(
            market_calendar_settings.primary_provider, 
            "No healthy calendar providers available."
        )

    async def execute(self, operation: Callable[[BaseCalendarProvider], Coroutine[Any, Any, Any]], operation_name: str = "unknown") -> Any:
        """Executes the operation on the active provider."""
        provider = self._get_active_provider()
        try:
            return await operation(provider)
        except Exception as e:
            logger.error(f"Provider {provider.name} failed during {operation_name}. Error: {str(e)}", exc_info=True)
            raise
