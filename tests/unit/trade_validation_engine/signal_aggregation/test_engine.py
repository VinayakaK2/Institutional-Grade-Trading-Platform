import pytest
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest
from backend.trade_validation_engine.signal_aggregation.di.container import SignalAggregationContainer
from backend.trade_validation_engine.signal_aggregation.exceptions.exceptions import InvalidAggregationRequestError

@pytest.fixture
def container():
    return SignalAggregationContainer()

@pytest.fixture
def valid_request():
    return SignalAggregationRequest(
        symbol="BTCUSD",
        timeframe="1H",
        dataset_version=1,
        universe_snapshot_version=1,
        watchlist_snapshot_version=1,
        trend_snapshot_version=1,
        consolidation_snapshot_version=1,
        liquidity_grab_snapshot_version=1
    )

@pytest.mark.asyncio
async def test_engine_execution_success(container, valid_request):
    snapshot = await container.engine.execute(valid_request)
    assert snapshot is not None
    assert snapshot.success is True
    assert len(snapshot.stage_results) == 6
    assert snapshot.aggregated_evidence is not None
    assert snapshot.aggregated_evidence.symbol == "BTCUSD"
    
    # Verify persistence
    persisted = await container.repository.get_by_id(snapshot.aggregation_id)
    assert persisted is not None
    assert persisted.aggregation_id == snapshot.aggregation_id

@pytest.mark.asyncio
async def test_engine_validation_failures(container, valid_request):
    with pytest.raises(InvalidAggregationRequestError, match="Symbol"):
        req = valid_request.model_copy(update={"symbol": ""})
        await container.engine.execute(req)
        
    with pytest.raises(InvalidAggregationRequestError, match="Symbol"):
        req = valid_request.model_copy(update={"timeframe": ""})
        await container.engine.execute(req)

    with pytest.raises(InvalidAggregationRequestError, match="Dataset version"):
        req = valid_request.model_copy(update={"dataset_version": 0})
        await container.engine.execute(req)
        
    with pytest.raises(InvalidAggregationRequestError, match="Universe snapshot"):
        req = valid_request.model_copy(update={"universe_snapshot_version": 0})
        await container.engine.execute(req)

    with pytest.raises(InvalidAggregationRequestError, match="Watchlist snapshot"):
        req = valid_request.model_copy(update={"watchlist_snapshot_version": 0})
        await container.engine.execute(req)

    with pytest.raises(InvalidAggregationRequestError, match="Trend snapshot"):
        req = valid_request.model_copy(update={"trend_snapshot_version": 0})
        await container.engine.execute(req)

    with pytest.raises(InvalidAggregationRequestError, match="Consolidation snapshot"):
        req = valid_request.model_copy(update={"consolidation_snapshot_version": 0})
        await container.engine.execute(req)

    with pytest.raises(InvalidAggregationRequestError, match="Liquidity Grab snapshot"):
        req = valid_request.model_copy(update={"liquidity_grab_snapshot_version": 0})
        await container.engine.execute(req)
