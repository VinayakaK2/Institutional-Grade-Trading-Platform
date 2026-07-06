"""
Tests for Provider contracts and mock implementations.
"""
import pytest
from backend.instrument.providers.mock_provider import MockSymbolProvider
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.models.instrument import Equity, InstrumentIdentity, InstrumentMetadata

@pytest.mark.asyncio
async def test_mock_provider():
    provider = MockSymbolProvider("test_mock")
    
    # Add dummy data
    provider.exchanges.append(
        ExchangeMetadata(code="TEST", name="Test Exchange", country_code="US", timezone="UTC")
    )
    
    equity = Equity(
        identity=InstrumentIdentity(symbol="SYM", exchange="TEST", internal_id="TEST:SYM"),
        metadata=InstrumentMetadata(name="Symbol", currency="USD", tick_size=0.01)
    )
    provider.instruments.append(equity)
    
    # Test fetch_exchanges
    exchanges = await provider.fetch_exchanges()
    assert len(exchanges) == 1
    assert exchanges[0].code == "TEST"
    
    # Test fetch_all_instruments (async generator)
    batches = []
    async for batch in provider.fetch_all_instruments():
        batches.append(batch)
        
    assert len(batches) == 1
    assert len(batches[0]) == 1
    assert batches[0][0].identity.internal_id == "TEST:SYM"
    
    # Test fetch_updates_since
    update_batches = []
    async for batch in provider.fetch_updates_since("1"):
        update_batches.append(batch)
        
    assert len(update_batches) == 1
