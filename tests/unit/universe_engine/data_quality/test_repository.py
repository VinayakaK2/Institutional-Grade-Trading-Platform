import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.infrastructure.database.orm.base import Base
from backend.universe_engine.data_quality.models import (
    CertifiedUniverse,
    DataQualityFilterConfiguration,
    DataQualityFilterStatistics,
    DataQualityRejectionDetail,
    DataQualityRejectionReason,
)
from backend.universe_engine.models.universe import UniverseInstrument
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.data_quality.repository import (
    PostgresDataQualityRepository,
)


@pytest_asyncio.fixture
async def async_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def sample_certified_universe():
    exchange = ExchangeReference(code="XNAS")
    symbol = SymbolReference(symbol="AAPL", exchange=exchange)
    instrument = UniverseInstrument(
        symbol=symbol,
        instrument_type="EQUITY",
        trading_status="ACTIVE",
        market_segment="EQUITY_CASH",
        is_delisted=False,
    )

    rej_symbol = SymbolReference(symbol="BAD", exchange=exchange)
    rejection = DataQualityRejectionDetail(
        instrument_symbol=rej_symbol.symbol,
        stage_name="MissingCandleDetection",
        reason=DataQualityRejectionReason.TOO_MANY_GAPS,
        measured_value="0.10",
        threshold="0.05",
    )

    return CertifiedUniverse(
        certified_universe_id="cert_uuid",
        parent_snapshot_id="parent_uuid",
        pipeline_version="1.0.0",
        config_hash="abc123hash",
        dataset_version="v1",
        created_at=datetime.now(timezone.utc),
        certified_symbols=[instrument],
        rejected_symbols=[rejection],
        configuration_snapshot=DataQualityFilterConfiguration(
            min_history_days=252,
            max_missing_candles_percentage=0.05,
            max_consecutive_suspensions=5,
            check_corporate_actions=True,
        ),
        statistics=DataQualityFilterStatistics(
            initial_instrument_count=2, final_certified_count=1, gap_rejections=1
        ),
    )


@pytest.mark.asyncio
async def test_postgres_repository_save_and_load(
    async_session_factory, sample_certified_universe
):
    repo = PostgresDataQualityRepository(async_session_factory)

    # Save
    await repo.save_certified_universe(sample_certified_universe)

    # Load
    loaded = await repo.load_certified_universe(
        sample_certified_universe.certified_universe_id
    )

    assert loaded is not None
    assert (
        loaded.certified_universe_id == sample_certified_universe.certified_universe_id
    )
    assert loaded.parent_snapshot_id == "parent_uuid"
    assert loaded.dataset_version == "v1"

    assert len(loaded.certified_symbols) == 1
    assert loaded.certified_symbols[0].symbol.symbol == "AAPL"

    assert len(loaded.rejected_symbols) == 1
    assert loaded.rejected_symbols[0].instrument_symbol == "BAD"
    assert loaded.rejected_symbols[0].reason == DataQualityRejectionReason.TOO_MANY_GAPS

    assert loaded.statistics.gap_rejections == 1
    assert loaded.configuration_snapshot.min_history_days == 252
