"""
Provider Registry
"""
from typing import Dict, Optional, List
from backend.market_data.provider.interface import BaseProvider
from backend.core.logger import get_logger

logger = get_logger(__name__)

class ProviderRegistry:
    """Central registry holding all instantiated market data providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        
    def register(self, provider: BaseProvider) -> None:
        """Registers a provider."""
        self._providers[provider.name] = provider
        logger.debug(f"Registered Market Data Provider: {provider.name}")
        
    def get(self, name: str) -> Optional[BaseProvider]:
        """Retrieves a provider by name."""
        return self._providers.get(name)
        
    def list_all(self) -> List[BaseProvider]:
        return list(self._providers.values())

# Global registry instance
provider_registry = ProviderRegistry()
