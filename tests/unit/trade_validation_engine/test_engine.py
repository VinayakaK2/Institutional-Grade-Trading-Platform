import pytest
import asyncio
from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.config.config import TradeValidationConfig
from backend.trade_validation_engine.models.models import TradeValidationRequest
from backend.trade_validation_engine.pipeline.pipeline import TradeValidationPipeline
from backend.trade_validation_engine.repository.memory import InMemoryTradeValidationRepository
from backend.trade_validation_engine.engine.engine import TradeValidationEngine
from backend.trade_validation_engine.exceptions.exceptions import InvalidExecutionContextError

@pytest.mark.asyncio
async def test_engine_successful_execution():
    context = TradeValidationExecutionContext(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig()
    )
    request = TradeValidationRequest(context=context)
    
    pipeline = TradeValidationPipeline(stages=[])
    repository = InMemoryTradeValidationRepository()
    engine = TradeValidationEngine(pipeline, repository)
    
    snapshot = await engine.execute(request)
    
    assert snapshot is not None
    assert snapshot.symbol == "BTCUSD"
    assert snapshot.pipeline_result.success is True
    
    # Verify persistence
    persisted = await repository.get_by_id(snapshot.snapshot_id)
    assert persisted is not None
    assert persisted.snapshot_id == snapshot.snapshot_id

@pytest.mark.asyncio
async def test_engine_structural_validation_failure():
    # Provide invalid context
    context = TradeValidationExecutionContext(
        symbol="", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig()
    )
    request = TradeValidationRequest(context=context)
    
    pipeline = TradeValidationPipeline(stages=[])
    repository = InMemoryTradeValidationRepository()
    engine = TradeValidationEngine(pipeline, repository)
    
    with pytest.raises(InvalidExecutionContextError):
        await engine.execute(request)
