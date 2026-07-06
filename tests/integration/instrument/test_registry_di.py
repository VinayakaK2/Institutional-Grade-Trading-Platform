"""
Tests for Registry Service / Facade.
"""
import pytest
from backend.instrument.service import SymbolRegistryService
from backend.instrument.registry.manager import SymbolRegistryManager
from backend.instrument.providers.mock_provider import MockSymbolProvider
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.models.instrument import Equity, InstrumentIdentity, InstrumentMetadata
from backend.instrument.contracts.search import SearchCriteria

@pytest.fixture
def registry_service():
    provider = MockSymbolProvider("mock1")
    provider.exchanges.append(
        ExchangeMetadata(code="NSE", name="NSE", country_code="IN", timezone="UTC")
    )
    provider.instruments.append(
        Equity(
            identity=InstrumentIdentity(symbol="TEST", exchange="NSE", internal_id="NSE:TEST"),
            metadata=InstrumentMetadata(name="Test Instrument", currency="INR", tick_size=0.05)
        )
    )
    
    manager = SymbolRegistryManager(providers=[provider])
    return SymbolRegistryService(manager)

@pytest.mark.asyncio
async def test_service_initialization(registry_service):
    await registry_service.initialize()
    
    # Check that search index is built and populated
    results = registry_service.search(SearchCriteria(query="TEST"))
    assert len(results) == 1
    assert results[0] == "NSE:TEST"
    
    # Check direct instrument fetch
    instr = await registry_service.get_instrument("NSE:TEST")
    assert instr is not None
    assert instr.identity.symbol == "TEST"

@pytest.mark.asyncio
async def test_service_incremental_refresh(registry_service):
    await registry_service.initialize()
    
    # Add a new instrument to provider
    provider = registry_service.manager.providers[0]
    provider.instruments.append(
        Equity(
            identity=InstrumentIdentity(symbol="NEW", exchange="NSE", internal_id="NSE:NEW"),
            metadata=InstrumentMetadata(name="New Instrument", currency="INR", tick_size=0.05)
        )
    )
    
    await registry_service.refresh_incremental()
    
    # Check search index got updated
    results = registry_service.search(SearchCriteria(query="NEW"))
    assert len(results) == 1
    assert results[0] == "NSE:NEW"

@pytest.mark.asyncio
async def test_service_full_refresh(registry_service):
    await registry_service.initialize()
    await registry_service.refresh_full()
    
    results = registry_service.search(SearchCriteria(query="TEST"))
    assert len(results) == 1
