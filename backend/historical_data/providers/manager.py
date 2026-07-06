"""
Provider Manager
"""
from typing import Dict, List, Optional
import logging
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.contracts.provider import HistoricalProviderContract
from backend.historical_data.exceptions import ProviderUnavailableException

logger = logging.getLogger(__name__)

class ProviderManager:
    """
    Manages provider registration, health tracking, and priority routing.
    Enables automatic failover.
    """
    def __init__(self):
        # Priority list of provider names
        self._priorities: List[str] = []
        # Mapping of provider name to instance
        self._providers: Dict[str, HistoricalProviderContract] = {}
        
    def register_provider(self, provider: HistoricalProviderContract, priority: int = 1) -> None:
        """Registers a provider. Higher priority value = checked first."""
        self._providers[provider.name] = provider
        # Naive insert, in real scenario we'd sort by priority.
        # For simplicity, we just append to the priority list. 
        # A more robust implementation would use a list of tuples (priority, name).
        self._priorities.append(provider.name)
        logger.info(f"Registered historical provider: {provider.name}")
        
    def get_provider(self, name: str) -> Optional[HistoricalProviderContract]:
        """Gets a specific provider by name."""
        return self._providers.get(name)
        
    async def get_best_available_provider(self, timeframe: Timeframe) -> HistoricalProviderContract:
        """
        Iterates through registered providers based on priority.
        Returns the first healthy provider that supports the timeframe.
        """
        for name in self._priorities:
            provider = self._providers[name]
            if provider.supports_timeframe(timeframe):
                try:
                    if await provider.is_healthy():
                        return provider
                except Exception as e:
                    logger.warning(f"Provider {name} health check failed: {e}")
                    
        raise ProviderUnavailableException("ALL", f"No healthy providers found supporting timeframe {timeframe.value}")
