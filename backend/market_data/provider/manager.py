"""
Provider Manager
Coordinates request failover across primary and secondary providers.
"""
from typing import List, Callable, Coroutine, Any, Optional
from backend.market_data.provider.interface import BaseProvider
from backend.market_data.provider.registry import ProviderRegistry, provider_registry as default_registry
from backend.market_data.config.settings import market_data_settings
from backend.market_data.exceptions import AllProvidersFailedException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class ProviderManager:
    """Manages provider selection and automatic failover."""
    
    def __init__(self, registry: Optional[ProviderRegistry] = None):
        self._registry = registry or default_registry
        
    def _get_execution_order(self) -> List[BaseProvider]:
        """Returns the list of providers in priority order (Primary -> Fallbacks)."""
        order = []
        
        # 1. Primary
        primary = self._registry.get(market_data_settings.primary_provider)
        if primary and primary.is_healthy:
            order.append(primary)
            
        # 2. Failovers
        for fallback_name in market_data_settings.failover_providers:
            fallback = self._registry.get(fallback_name)
            if fallback and fallback.is_healthy and fallback not in order:
                order.append(fallback)
                
        # 3. If primary was unhealthy, it might still be added last if we want to force a try
        # But for circuit breaker safety, we skip unhealthy providers entirely.
        
        return order

    async def execute_with_failover(
        self, 
        operation: Callable[[BaseProvider], Coroutine[Any, Any, Any]],
        operation_name: str = "unknown"
    ) -> Any:
        """
        Attempts to execute the given operation against providers in priority order.
        If a provider fails, it logs a warning and tries the next one.
        """
        providers = self._get_execution_order()
        
        if not providers:
            logger.critical("No healthy market data providers available.")
            raise AllProvidersFailedException("No healthy providers available for execution.")
            
        errors = []
        
        for provider in providers:
            try:
                logger.debug(f"Attempting {operation_name} using provider: {provider.name}")
                result = await operation(provider)
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed during {operation_name}. Error: {str(e)}")
                errors.append(f"{provider.name}: {str(e)}")
                continue # Try next provider
                
        # If we reach here, all providers failed
        logger.error(f"All providers failed for {operation_name}. Errors: {errors}")
        raise AllProvidersFailedException(f"All {len(providers)} providers failed: {errors}")
