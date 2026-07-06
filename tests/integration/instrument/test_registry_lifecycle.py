"""
Tests for Registry Lifecycle (Initial Load, Refresh).
"""
import pytest
from backend.instrument.registry.manager import SymbolRegistryManager
from backend.instrument.providers.mock_provider import MockSymbolProvider
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.models.instrument import Equity, InstrumentIdentity, InstrumentMetadata

@pytest.fixture
def mock_provider():
    provider = MockSymbolProvider("mock1")
    provider.exchanges.append(
        ExchangeMetadata(code="NSE", name="NSE", country_code="IN", timezone="UTC")
    )
    provider.instruments.append(
        Equity(
            identity=InstrumentIdentity(symbol="TEST", exchange="NSE", internal_id="NSE:TEST"),
            metadata=InstrumentMetadata(name="Test", currency="INR", tick_size=0.05)
        )
    )
    return provider

@pytest.mark.asyncio
async def test_initial_load(mock_provider):
    manager = SymbolRegistryManager(providers=[mock_provider])
    await manager.load_initial()
    
    snapshot = manager.get_snapshot()
    assert snapshot.version == 1
    assert len(snapshot.exchanges) == 1
    assert len(snapshot.instruments) == 1
    
    instr = await manager.get_instrument("NSE:TEST")
    assert instr is not None

@pytest.mark.asyncio
async def test_incremental_refresh(mock_provider):
    manager = SymbolRegistryManager(providers=[mock_provider])
    await manager.load_initial()
    
    # Add a new instrument to provider for incremental refresh
    mock_provider.instruments.append(
        Equity(
            identity=InstrumentIdentity(symbol="NEW", exchange="NSE", internal_id="NSE:NEW"),
            metadata=InstrumentMetadata(name="New", currency="INR", tick_size=0.05)
        )
    )
    
    await manager.refresh_incremental()
    
    snapshot = manager.get_snapshot()
    assert snapshot.version == 2
    assert len(snapshot.instruments) == 2
    
    new_instr = await manager.get_instrument("NSE:NEW")
    assert new_instr is not None

@pytest.mark.asyncio
async def test_full_refresh(mock_provider):
    manager = SymbolRegistryManager(providers=[mock_provider])
    await manager.load_initial()
    
    await manager.refresh_full()
    
    snapshot = manager.get_snapshot()
    assert snapshot.version == 2
