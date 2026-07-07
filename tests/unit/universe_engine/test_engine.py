import pytest
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment
from backend.universe_engine.contracts.provider import IUniverseProvider
from backend.universe_engine.engine.engine import UniverseEngine
from backend.universe_engine.models.config import UniverseSettings, ValidationSettings, PipelineSettings
from backend.universe_engine.validation.validators import UniverseValidator
from backend.universe_engine.pipeline.pipeline import UniverseExecutionPipeline
from backend.universe_engine.repository.repository import InMemoryUniverseRepository
from backend.universe_engine.models.universe import ValidationStatus

class MockProvider(IUniverseProvider):
    @property
    def provider_name(self) -> str:
        return "MockProvider"
        
    async def fetch_universe(self):
        return [
            UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False),
            UniverseInstrument(symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)
        ]

@pytest.fixture
def mock_engine():
    settings = UniverseSettings(
        pipeline=PipelineSettings(),
        validation=ValidationSettings()
    )
    provider = MockProvider()
    pipeline = UniverseExecutionPipeline(settings.pipeline)
    repository = InMemoryUniverseRepository()
    validator = UniverseValidator(settings.validation)
    
    return UniverseEngine(
        settings=settings,
        provider=provider,
        pipeline=pipeline,
        repository=repository,
        validator=validator
    )

@pytest.mark.asyncio
async def test_universe_engine_success(mock_engine):
    run_id = "test-run-1"
    
    result = await mock_engine.generate_universe(run_id)
    
    snapshot = result.snapshot
    assert snapshot.version == 1
    assert snapshot.provider == "MockProvider"
    assert snapshot.symbol_count == 2
    assert snapshot.validation_status == ValidationStatus.PASSED
    
    # Verify repository saved the snapshot
    loaded = await mock_engine._repository.load_snapshot(snapshot.snapshot_id)
    assert loaded is not None
    assert loaded.snapshot_id == snapshot.snapshot_id

@pytest.mark.asyncio
async def test_universe_engine_version_increment(mock_engine):
    # Run once
    result1 = await mock_engine.generate_universe("run-1")
    assert result1.snapshot.version == 1
    
    # Run twice
    result2 = await mock_engine.generate_universe("run-2")
    assert result2.snapshot.version == 2

