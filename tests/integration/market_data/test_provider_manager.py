"""
Integration Tests for Provider Manager (Failover Logic)
"""
import pytest
from backend.market_data.provider.manager import ProviderManager
from backend.market_data.provider.registry import ProviderRegistry
from backend.market_data.config.settings import market_data_settings
from backend.market_data.exceptions import AllProvidersFailedException

class MockProvider:
    def __init__(self, name: str, is_healthy: bool, should_fail: bool):
        self._name = name
        self._is_healthy = is_healthy
        self.should_fail = should_fail
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def is_healthy(self) -> bool:
        return self._is_healthy

@pytest.mark.asyncio
async def test_provider_manager_all_fail():
    registry = ProviderRegistry()
    primary = MockProvider("primary", True, True)
    registry.register(primary)
    
    market_data_settings.primary_provider = "primary"
    market_data_settings.failover_providers = []
    
    manager = ProviderManager(registry=registry)
    
    async def dummy_operation(provider):
        raise ValueError(f"Provider {provider.name} failed internally")
        
    with pytest.raises(AllProvidersFailedException):
        await manager.execute_with_failover(dummy_operation)

@pytest.mark.asyncio
async def test_provider_manager_no_healthy():
    registry = ProviderRegistry()
    primary = MockProvider("primary", False, False)
    registry.register(primary)
    
    market_data_settings.primary_provider = "primary"
    market_data_settings.failover_providers = []
    
    manager = ProviderManager(registry=registry)
    
    async def dummy_operation(provider):
        return True
        
    with pytest.raises(AllProvidersFailedException):
        await manager.execute_with_failover(dummy_operation)

@pytest.mark.asyncio
async def test_provider_manager_failover():
    registry = ProviderRegistry()
    
    # Primary is healthy but throws an exception during execution
    primary = MockProvider("primary", True, True)
    # Secondary is healthy and succeeds
    secondary = MockProvider("secondary", True, False)
    
    registry.register(primary)
    registry.register(secondary)
    
    market_data_settings.primary_provider = "primary"
    market_data_settings.failover_providers = ["secondary"]
    
    manager = ProviderManager(registry=registry)
    
    async def dummy_operation(provider):
        if provider.should_fail:
            raise ValueError(f"Provider {provider.name} failed internally")
        return f"{provider.name}_success"
        
    # Execution should fail on primary, and succeed on secondary
    result = await manager.execute_with_failover(dummy_operation)
    assert result == "secondary_success"

@pytest.mark.asyncio
async def test_execute_with_failover_all_providers_fail():
    registry = ProviderRegistry()
    
    primary = MockProvider("primary", True, True)
    secondary = MockProvider("secondary", True, True)
    
    registry.register(primary)
    registry.register(secondary)
    
    market_data_settings.primary_provider = "primary"
    market_data_settings.failover_providers = ["secondary"]
    
    manager = ProviderManager(registry=registry)
    
    async def dummy_operation(provider):
        raise ValueError("Fail")
        
    with pytest.raises(AllProvidersFailedException):
        await manager.execute_with_failover(dummy_operation)
