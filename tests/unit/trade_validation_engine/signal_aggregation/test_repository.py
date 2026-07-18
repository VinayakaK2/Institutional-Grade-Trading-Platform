import pytest
import time
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot, SignalAggregationMetadata, AggregatedTradeEvidence
from backend.trade_validation_engine.signal_aggregation.repository.memory import InMemorySignalAggregationRepository
from backend.trade_validation_engine.signal_aggregation.query_service.memory import InMemorySignalAggregationQueryService
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import RepositoryError

def create_mock_snapshot(symbol: str, timeframe: str, dataset_version: int = 1) -> SignalAggregationSnapshot:
    time.sleep(0.01)
    
    aggregation_id = SignalAggregationSnapshot.generate_id(
        symbol=symbol, dataset_version=dataset_version, wl_version=1, t_version=1, c_version=1, lg_version=1, config_hash="test"
    )
    
    evidence = AggregatedTradeEvidence(
        symbol=symbol,
        timeframe=timeframe,
        dataset_version=dataset_version,
        configuration_hash="test"
    )
    
    return SignalAggregationSnapshot(
        aggregation_id=aggregation_id,
        symbol=symbol,
        timeframe=timeframe,
        success=True,
        stage_results=[],
        aggregated_evidence=evidence,
        metadata=SignalAggregationMetadata(execution_duration_ms=10)
    )

@pytest.mark.asyncio
async def test_repository_save_and_get():
    repo = InMemorySignalAggregationRepository()
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    
    await repo.save(snapshot)
    
    assert await repo.exists(snapshot.aggregation_id) is True
    retrieved = await repo.get_by_id(snapshot.aggregation_id)
    assert retrieved is not None
    assert retrieved.aggregation_id == snapshot.aggregation_id

@pytest.mark.asyncio
async def test_repository_immutability():
    repo = InMemorySignalAggregationRepository()
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    
    await repo.save(snapshot)
    
    with pytest.raises(RepositoryError, match="already exists"):
        await repo.save(snapshot)

@pytest.mark.asyncio
async def test_query_service_get_latest_by_symbol():
    repo = InMemorySignalAggregationRepository()
    qs = InMemorySignalAggregationQueryService(repo._storage)
    
    s1 = create_mock_snapshot("BTCUSD", "1H", dataset_version=1)
    s2 = create_mock_snapshot("BTCUSD", "1H", dataset_version=2)
    s3 = create_mock_snapshot("ETHUSD", "1H", dataset_version=1)
    
    await repo.save(s1)
    await repo.save(s2)
    await repo.save(s3)
    
    latest_btc = await qs.get_latest_by_symbol("BTCUSD", "1H")
    assert latest_btc is not None
    assert latest_btc.aggregation_id == s2.aggregation_id

@pytest.mark.asyncio
async def test_query_service_list_paginated():
    repo = InMemorySignalAggregationRepository()
    qs = InMemorySignalAggregationQueryService(repo._storage)
    
    s1 = create_mock_snapshot("BTCUSD", "1H", dataset_version=1)
    s2 = create_mock_snapshot("BTCUSD", "4H", dataset_version=2)
    
    await repo.save(s1)
    await repo.save(s2)
    
    results = await qs.list_paginated("BTCUSD", limit=1, offset=0)
    assert len(results) == 1
    
    results2 = await qs.list_paginated("BTCUSD", limit=1, offset=1)
    assert len(results2) == 1

@pytest.mark.asyncio
async def test_query_service_get_by_dataset_version():
    repo = InMemorySignalAggregationRepository()
    qs = InMemorySignalAggregationQueryService(repo._storage)
    
    s1 = create_mock_snapshot("BTCUSD", "1H", dataset_version=5)
    
    await repo.save(s1)
    
    results = await qs.get_by_dataset_version(5)
    assert len(results) == 1
    assert results[0].aggregation_id == s1.aggregation_id

@pytest.mark.asyncio
async def test_postgres_stubs():
    from backend.trade_validation_engine.signal_aggregation.repository.postgres import PostgreSQLSignalAggregationRepository
    from backend.trade_validation_engine.signal_aggregation.query_service.postgres import PostgreSQLSignalAggregationQueryService
    
    repo = PostgreSQLSignalAggregationRepository("mock")
    qs = PostgreSQLSignalAggregationQueryService("mock")
    
    snapshot = create_mock_snapshot("BTCUSD", "1H")
    await repo.save(snapshot)
    assert await repo.get_by_id(snapshot.aggregation_id) is None
    assert await repo.exists(snapshot.aggregation_id) is False
    
    assert await qs.get_by_aggregation_id(snapshot.aggregation_id) is None
    assert await qs.get_latest_by_symbol("BTCUSD", "1H") is None
    assert await qs.list_paginated("BTCUSD") == []
    assert await qs.get_by_dataset_version(1) == []
