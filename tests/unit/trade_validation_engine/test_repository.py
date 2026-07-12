import pytest
import asyncio
import time
from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.config.config import TradeValidationConfig
from backend.trade_validation_engine.models.models import TradeValidationSnapshot, ValidationPipelineResult, TradeValidationMetadata
from backend.trade_validation_engine.repository.memory import InMemoryTradeValidationRepository
from backend.trade_validation_engine.query_service.memory import InMemoryTradeValidationQueryService
from backend.trade_validation_engine.exceptions.exceptions import RepositoryError
from backend.trade_validation_engine.di.container import TradeValidationContainer

def create_mock_snapshot(symbol: str, timeframe: str, trend_version: int = 1) -> TradeValidationSnapshot:
    time.sleep(0.01) # Ensure unique timestamps on Windows
    context = TradeValidationExecutionContext(
        symbol=symbol, timeframe=timeframe, dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=trend_version,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig()
    )
    snapshot_id = TradeValidationSnapshot.generate_id(
        symbol=symbol, timeframe=timeframe, dataset_version=1, wl_version=1,
        t_version=trend_version, c_version=1, lg_version=1
    )
    return TradeValidationSnapshot(
        snapshot_id=snapshot_id,
        symbol=symbol,
        timeframe=timeframe,
        pipeline_result=ValidationPipelineResult(success=True),
        context=context,
        metadata=TradeValidationMetadata(execution_duration_ms=100)
    )

@pytest.mark.asyncio
async def test_repository_save_and_get():
    repo = InMemoryTradeValidationRepository()
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    
    await repo.save(snapshot)
    retrieved = await repo.get_by_id(snapshot.snapshot_id)
    
    assert retrieved is not None
    assert retrieved.snapshot_id == snapshot.snapshot_id
    
@pytest.mark.asyncio
async def test_repository_insert_only():
    repo = InMemoryTradeValidationRepository()
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    
    await repo.save(snapshot)
    
    with pytest.raises(RepositoryError, match="already exists"):
        await repo.save(snapshot)

@pytest.mark.asyncio
async def test_query_service_get_latest_by_symbol():
    repo = InMemoryTradeValidationRepository()
    qs = InMemoryTradeValidationQueryService(repo._storage)
    
    # Save a few snapshots, modifying the trend version to make unique IDs
    s1 = create_mock_snapshot("BTCUSD", "1H", trend_version=1)
    s2 = create_mock_snapshot("BTCUSD", "1H", trend_version=2)
    s3 = create_mock_snapshot("ETHUSD", "1H", trend_version=1)
    
    await repo.save(s1)
    await asyncio.sleep(0.01) # Ensure timestamps are different
    await repo.save(s2)
    await repo.save(s3)
    
    latest_btc = await qs.get_latest_by_symbol("BTCUSD", "1H")
    assert latest_btc is not None
    # Since s2 was saved later (mocking), it should have a later timestamp
    # Actually create_mock_snapshot uses default_factory=datetime.now so s2 is definitely later
    assert latest_btc.snapshot_id == s2.snapshot_id
    
@pytest.mark.asyncio
async def test_query_service_get_by_snapshot_version():
    repo = InMemoryTradeValidationRepository()
    qs = InMemoryTradeValidationQueryService(repo._storage)
    
    # Use timeframe to differentiate the ID while keeping the same trend_version
    s1 = create_mock_snapshot("BTCUSD", "1H", trend_version=5)
    s2 = create_mock_snapshot("BTCUSD", "4H", trend_version=5)
    s3 = create_mock_snapshot("BTCUSD", "1D", trend_version=6) 
    
    await repo.save(s1)
    await repo.save(s2)
    await repo.save(s3)
    
    results = await qs.get_by_snapshot_version("BTCUSD", "1H", "parent_trend_snapshot_version", 5)
    assert len(results) == 1
    assert results[0].snapshot_id == s1.snapshot_id
    
@pytest.mark.asyncio
async def test_query_service_list_paginated():
    repo = InMemoryTradeValidationRepository()
    qs = InMemoryTradeValidationQueryService(repo._storage)
    
    s1 = create_mock_snapshot("BTCUSD", "1m", trend_version=1)
    s2 = create_mock_snapshot("BTCUSD", "5m", trend_version=2)
    s3 = create_mock_snapshot("BTCUSD", "15m", trend_version=3)
    
    await repo.save(s1)
    await repo.save(s2)
    await repo.save(s3)
    
    results = await qs.list_paginated("BTCUSD", limit=2, offset=0)
    assert len(results) == 2
    
    results_offset = await qs.list_paginated("BTCUSD", limit=2, offset=2)
    assert len(results_offset) == 1

def test_container_initialization():
    container = TradeValidationContainer()
    assert container.engine is not None
    assert container.repository is not None
    assert container.query_service is not None

@pytest.mark.asyncio
async def test_postgres_repository_stubs():
    from backend.trade_validation_engine.repository.postgres import PostgreSQLTradeValidationRepository
    repo = PostgreSQLTradeValidationRepository("mock_conn")
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    await repo.save(snapshot) # Should not raise
    res = await repo.get_by_id(snapshot.snapshot_id)
    assert res is None

@pytest.mark.asyncio
async def test_postgres_query_service_stubs():
    from backend.trade_validation_engine.query_service.postgres import PostgreSQLTradeValidationQueryService
    qs = PostgreSQLTradeValidationQueryService("mock_conn")
    
    assert await qs.get_by_id("123") is None
    assert await qs.get_latest_by_symbol("BTCUSD", "1H") is None
    assert await qs.get_by_snapshot_version("BTCUSD", "1H", "version", 1) == []
    assert await qs.list_paginated("BTCUSD") == []
