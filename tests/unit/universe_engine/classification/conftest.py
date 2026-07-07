import pytest
from datetime import datetime, timezone
from typing import Optional

from backend.universe_engine.models.universe import (
    UniverseInstrument,
    InstrumentType,
    TradingStatus,
    MarketSegment,
)
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.contracts.classification import IClassificationDataProvider
from backend.universe_engine.data_quality.models import CertifiedUniverse, DataQualityFilterConfiguration, DataQualityFilterStatistics
from backend.universe_engine.classification.pipeline import UniverseClassificationPipeline
from backend.universe_engine.classification.engine import UniverseClassificationEngine
from backend.universe_engine.classification.repository import InMemoryClassificationRepository
from backend.universe_engine.classification.models import UniverseClassificationConfiguration
from backend.universe_engine.classification.stages import (
    SectorClassificationStage,
    IndustryClassificationStage,
    MarketCapClassificationStage,
    LiquidityClassificationStage,
    DataQualityClassificationStage,
)

class MockClassificationDataProvider(IClassificationDataProvider):
    def __init__(self):
        self.sectors = {}
        self.industries = {}
        self.market_caps = {}
        self.should_fail = False

    async def get_sector(self, instrument: UniverseInstrument) -> Optional[str]:
        if self.should_fail:
            raise Exception("Provider error")
        return self.sectors.get(instrument.symbol.symbol)

    async def get_industry(self, instrument: UniverseInstrument) -> Optional[str]:
        if self.should_fail:
            raise Exception("Provider error")
        return self.industries.get(instrument.symbol.symbol)

    async def get_market_cap(self, instrument: UniverseInstrument) -> Optional[float]:
        if self.should_fail:
            raise Exception("Provider error")
        return self.market_caps.get(instrument.symbol.symbol)


@pytest.fixture
def mock_classification_provider():
    return MockClassificationDataProvider()

@pytest.fixture
def sample_instrument_1():
    return UniverseInstrument(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        instrument_type=InstrumentType.EQUITY,
        trading_status=TradingStatus.ACTIVE,
        market_segment=MarketSegment.EQUITY_CASH,
        is_delisted=False
    )

@pytest.fixture
def sample_instrument_2():
    return UniverseInstrument(
        symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")),
        instrument_type=InstrumentType.EQUITY,
        trading_status=TradingStatus.ACTIVE,
        market_segment=MarketSegment.EQUITY_CASH,
        is_delisted=False
    )

@pytest.fixture
def parent_certified_universe(sample_instrument_1, sample_instrument_2):
    return CertifiedUniverse(
        certified_universe_id="cert_uuid",
        parent_snapshot_id="snapshot_uuid",
        pipeline_version="1.0.0",
        config_hash="abc",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc),
        certified_symbols=[sample_instrument_1, sample_instrument_2],
        rejected_symbols=[],
        configuration_snapshot=DataQualityFilterConfiguration(),
        statistics=DataQualityFilterStatistics()
    )

@pytest.fixture
def parent_liquidity_metrics():
    return {
        "AAPL": {"average_daily_volume": 6_000_000.0},
        "MSFT": {"average_daily_volume": 500_000.0}
    }



@pytest.fixture
def test_engine(mock_classification_provider):
    config = UniverseClassificationConfiguration()
    pipeline = UniverseClassificationPipeline()
    pipeline.register_stage(SectorClassificationStage())
    pipeline.register_stage(IndustryClassificationStage())
    pipeline.register_stage(MarketCapClassificationStage())
    pipeline.register_stage(LiquidityClassificationStage())
    pipeline.register_stage(DataQualityClassificationStage())

    repo = InMemoryClassificationRepository()
    
    return UniverseClassificationEngine(
        config=config,
        pipeline=pipeline,
        data_provider=mock_classification_provider,
        repository=repo,
        pipeline_version="1.0.0"
    )
