import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment
from backend.universe_engine.classification.models import (
    ClassifiedSymbol, 
    MarketCapClassification, 
    LiquidityClassification, 
    DataQualityClassification,
    ClassifiedUniverse,
    UniverseClassificationStatistics,
    UniverseClassificationConfiguration
)
from backend.universe_engine.optimization.repository import InMemoryOptimizationRepository
from backend.universe_engine.optimization.pipeline import UniverseOptimizationPipeline
from backend.universe_engine.optimization.engine import UniverseOptimizationEngine
from backend.universe_engine.optimization.models import UniverseOptimizationConfiguration

@pytest.fixture
def mock_classified_symbols():
    return [
        ClassifiedSymbol(
            symbol=UniverseInstrument(
                symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
                instrument_type=InstrumentType.EQUITY,
                trading_status=TradingStatus.ACTIVE,
                market_segment=MarketSegment.EQUITY_CASH,
                is_delisted=False
            ),
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=MarketCapClassification.LARGE,
            liquidity=LiquidityClassification.HIGH,
            data_quality=DataQualityClassification.CERTIFIED
        ),
        ClassifiedSymbol(
            symbol=UniverseInstrument(
                symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")),
                instrument_type=InstrumentType.EQUITY,
                trading_status=TradingStatus.ACTIVE,
                market_segment=MarketSegment.EQUITY_CASH,
                is_delisted=False
            ),
            sector="Technology",
            industry="Software",
            market_cap=MarketCapClassification.LARGE,
            liquidity=LiquidityClassification.HIGH,
            data_quality=DataQualityClassification.CERTIFIED
        ),
        ClassifiedSymbol(
            symbol=UniverseInstrument(
                symbol=SymbolReference(symbol="PENNY", exchange=ExchangeReference(code="OTC")),
                instrument_type=InstrumentType.EQUITY,
                trading_status=TradingStatus.ACTIVE,
                market_segment=MarketSegment.EQUITY_CASH,
                is_delisted=False
            ),
            sector="Finance",
            industry="Banks",
            market_cap=MarketCapClassification.SMALL,
            liquidity=LiquidityClassification.LOW,
            data_quality=DataQualityClassification.CERTIFIED
        )
    ]

@pytest.fixture
def mock_classified_universe(mock_classified_symbols):
    return ClassifiedUniverse(
        classified_universe_id="mock_class_id",
        parent_certified_universe_id="mock_cert_id",
        pipeline_version="1.0.0",
        config_hash="mock_hash",
        created_at=datetime.now(timezone.utc),
        configuration_snapshot=UniverseClassificationConfiguration(),
        statistics=UniverseClassificationStatistics(total_symbols=len(mock_classified_symbols)),
        classified_symbols=mock_classified_symbols
    )

@pytest.fixture
def test_engine():
    config = UniverseOptimizationConfiguration(
        enable_incremental=True,
        enable_batching=True,
        enable_parallel=True,
        batch_size=2,
        max_workers=2
    )
    pipeline = UniverseOptimizationPipeline()
    repo = InMemoryOptimizationRepository()
    
    return UniverseOptimizationEngine(
        config=config,
        pipeline=pipeline,
        repository=repo,
        pipeline_version="1.0.0"
    )
