import pytest
from backend.trade_validation_engine.trade_decision.di.container import TradeDecisionContainer
from tests.unit.trade_validation_engine.trade_decision.conftest import MockValidStage

@pytest.mark.asyncio
async def test_repository_round_trip(valid_context, mock_validation_report):
    container = TradeDecisionContainer()
    container.pipeline.register_stage(MockValidStage())
    engine = container.engine()
    
    snapshot = await engine.execute(valid_context, mock_validation_report)
    
    # Save already happens in engine, but let's test repository load
    loaded = await container.repository.load(snapshot.decision_id)
    assert loaded is not None
    assert loaded.decision_id == snapshot.decision_id
    assert loaded.symbol == snapshot.symbol
    assert loaded.dataset_version == snapshot.dataset_version
    
    exists = await container.repository.exists(snapshot.decision_id)
    assert exists is True
    
    query1 = await container.repository.query_by_symbol(snapshot.symbol)
    assert len(query1) == 1
    
    query2 = await container.repository.query_by_timeframe(snapshot.timeframe)
    assert len(query2) == 1
    
    query3 = await container.repository.query_by_dataset_version(snapshot.dataset_version)
    assert len(query3) == 1
    
    query4 = await container.repository.query_by_validation_report(snapshot.validation_report_version)
    assert len(query4) == 1
    
    latest = await container.repository.load_latest(snapshot.symbol, snapshot.timeframe)
    assert latest is not None
    
    # Query service tests
    q_latest = await container.query_service.get_latest_by_symbol(snapshot.symbol)
    assert q_latest is not None
    
    q_by_id = await container.query_service.get_by_decision_id(snapshot.decision_id)
    assert q_by_id is not None
    
    q_dataset = await container.query_service.query_by_dataset_version(snapshot.dataset_version)
    assert len(q_dataset) == 1
