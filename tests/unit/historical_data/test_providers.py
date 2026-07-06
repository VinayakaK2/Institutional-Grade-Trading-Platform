import pytest
from backend.historical_data.providers.manager import ProviderManager
from backend.historical_data.providers.mock_provider import MockHistoricalProvider
from backend.market_data.models.timeframe import Timeframe
from backend.historical_data.exceptions import ProviderUnavailableException

@pytest.mark.asyncio
async def test_provider_manager_routing():
    manager = ProviderManager()
    
    # Healthy provider
    p1 = MockHistoricalProvider("p1", healthy=True)
    # Unhealthy provider
    p2 = MockHistoricalProvider("p2", healthy=False)
    
    manager.register_provider(p2)
    manager.register_provider(p1)
    
    # Should skip p2 (unhealthy) and select p1
    selected = await manager.get_best_available_provider(Timeframe.D1)
    assert selected.name == "p1"

@pytest.mark.asyncio
async def test_provider_manager_all_unhealthy():
    manager = ProviderManager()
    p1 = MockHistoricalProvider("p1", healthy=False)
    manager.register_provider(p1)
    
    with pytest.raises(ProviderUnavailableException):
        await manager.get_best_available_provider(Timeframe.D1)
