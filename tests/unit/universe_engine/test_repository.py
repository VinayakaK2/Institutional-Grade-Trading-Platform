import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
import uuid
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment
from backend.universe_engine.repository.repository import PostgreSQLUniverseRepository, InMemoryUniverseRepository
from backend.universe_engine.models.universe import UniverseSnapshot, ValidationStatus
from backend.universe_engine.models.exceptions import UniverseRepositoryError
from backend.infrastructure.database.orm.universe import UniverseSnapshotModel

@pytest.fixture
def mock_session_factory():
    session_mock = AsyncMock()
    session_mock.__aenter__.return_value = session_mock
    
    begin_mock = AsyncMock()
    begin_mock.__aenter__.return_value = begin_mock
    
    # session.begin() is synchronous, returns an async context manager
    session_mock.begin = MagicMock(return_value=begin_mock)
    
    # session.add is synchronous
    session_mock.add = MagicMock()
    
    factory_mock = MagicMock(return_value=session_mock)
    return factory_mock, session_mock

@pytest.fixture
def sample_snapshot():
    return UniverseSnapshot(
        snapshot_id=str(uuid.uuid4()),
        version=1,
        provider="TestProvider",
        created_at=datetime.now(timezone.utc),
        symbol_count=1,
        instruments=[UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)],
        metadata={"test": True},
        pipeline_version="1.0.0",
        validation_status=ValidationStatus.PASSED
    )

@pytest.mark.asyncio
async def test_postgres_repo_save_snapshot_success(mock_session_factory, sample_snapshot):
    factory_mock, session_mock = mock_session_factory
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    await repo.save_snapshot(sample_snapshot)
    
    session_mock.add.assert_called_once()
    added_model = session_mock.add.call_args[0][0]
    assert added_model.snapshot_id == sample_snapshot.snapshot_id

@pytest.mark.asyncio
async def test_postgres_repo_save_snapshot_error(mock_session_factory, sample_snapshot):
    factory_mock, session_mock = mock_session_factory
    session_mock.add.side_effect = Exception("DB Error")
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    with pytest.raises(UniverseRepositoryError) as exc:
        await repo.save_snapshot(sample_snapshot)
        
    assert "Database error while saving snapshot" in str(exc.value)

@pytest.mark.asyncio
async def test_postgres_repo_load_snapshot_success(mock_session_factory, sample_snapshot):
    factory_mock, session_mock = mock_session_factory
    
    # Setup mock result for execute().scalar_one_or_none()
    mock_result = MagicMock()
    
    # Create an ORM model representation of the snapshot
    orm_model = UniverseSnapshotModel(
        snapshot_id=sample_snapshot.snapshot_id,
        version=sample_snapshot.version,
        provider=sample_snapshot.provider,
        created_at=sample_snapshot.created_at,
        symbol_count=sample_snapshot.symbol_count,
        instruments=[sym.model_dump(mode="json") for sym in sample_snapshot.instruments],
        metadata_col=sample_snapshot.metadata,
        pipeline_version=sample_snapshot.pipeline_version,
        validation_status=sample_snapshot.validation_status.value
    )
    
    mock_result.scalar_one_or_none.return_value = orm_model
    session_mock.execute.return_value = mock_result
    
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    loaded = await repo.load_snapshot(sample_snapshot.snapshot_id)
    assert loaded is not None
    assert loaded.snapshot_id == sample_snapshot.snapshot_id

@pytest.mark.asyncio
async def test_postgres_repo_load_snapshot_none(mock_session_factory):
    factory_mock, session_mock = mock_session_factory
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session_mock.execute.return_value = mock_result
    
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    loaded = await repo.load_snapshot("does-not-exist")
    assert loaded is None

@pytest.mark.asyncio
async def test_postgres_repo_load_snapshot_error(mock_session_factory):
    factory_mock, session_mock = mock_session_factory
    session_mock.execute.side_effect = Exception("DB Error")
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    with pytest.raises(UniverseRepositoryError) as exc:
        await repo.load_snapshot("test-id")
        
    assert "Database error while loading snapshot" in str(exc.value)

@pytest.mark.asyncio
async def test_postgres_repo_load_latest_snapshot_success(mock_session_factory, sample_snapshot):
    factory_mock, session_mock = mock_session_factory
    
    mock_result = MagicMock()
    orm_model = UniverseSnapshotModel(
        snapshot_id=sample_snapshot.snapshot_id,
        version=sample_snapshot.version,
        provider=sample_snapshot.provider,
        created_at=sample_snapshot.created_at,
        symbol_count=sample_snapshot.symbol_count,
        instruments=[sym.model_dump(mode="json") for sym in sample_snapshot.instruments],
        metadata_col=sample_snapshot.metadata,
        pipeline_version=sample_snapshot.pipeline_version,
        validation_status=sample_snapshot.validation_status.value
    )
    mock_result.scalar_one_or_none.return_value = orm_model
    session_mock.execute.return_value = mock_result
    
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    loaded = await repo.load_latest_snapshot()
    assert loaded is not None
    assert loaded.snapshot_id == sample_snapshot.snapshot_id

@pytest.mark.asyncio
async def test_postgres_repo_load_latest_snapshot_none(mock_session_factory):
    factory_mock, session_mock = mock_session_factory
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session_mock.execute.return_value = mock_result
    
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    loaded = await repo.load_latest_snapshot()
    assert loaded is None

@pytest.mark.asyncio
async def test_postgres_repo_load_latest_snapshot_error(mock_session_factory):
    factory_mock, session_mock = mock_session_factory
    session_mock.execute.side_effect = Exception("DB Error")
    repo = PostgreSQLUniverseRepository(factory_mock)
    
    with pytest.raises(UniverseRepositoryError) as exc:
        await repo.load_latest_snapshot()
        
    assert "Database error while loading latest snapshot" in str(exc.value)

@pytest.mark.asyncio
async def test_in_memory_repository_save_load(sample_snapshot):
    repo = InMemoryUniverseRepository()
    
    await repo.save_snapshot(sample_snapshot)
    loaded = await repo.load_snapshot(sample_snapshot.snapshot_id)
    
    assert loaded is not None
    assert loaded.snapshot_id == sample_snapshot.snapshot_id
    assert loaded.symbol_count == 1
    assert loaded.instruments[0].symbol.symbol == "AAPL"

@pytest.mark.asyncio
async def test_in_memory_repository_load_latest(sample_snapshot):
    repo = InMemoryUniverseRepository()
    
    await repo.save_snapshot(sample_snapshot)
    
    # Create newer snapshot
    newer_snapshot = UniverseSnapshot(
        snapshot_id=str(uuid.uuid4()),
        version=2,
        provider="TestProvider",
        created_at=datetime.now(timezone.utc), # Slightly later due to execution time
        symbol_count=2,
        instruments=[
            UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False),
            UniverseInstrument(symbol=SymbolReference(symbol="MSFT", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)
        ],
        metadata={"test": True},
        pipeline_version="1.0.0",
        validation_status=ValidationStatus.PASSED
    )
    
    await repo.save_snapshot(newer_snapshot)
    
    latest = await repo.load_latest_snapshot()
    
    assert latest is not None
    assert latest.version == 2
    assert latest.snapshot_id == newer_snapshot.snapshot_id

