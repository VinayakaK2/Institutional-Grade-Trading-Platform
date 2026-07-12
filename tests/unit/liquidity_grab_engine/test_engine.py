import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration
from backend.liquidity_grab_engine.models.models import (
    LiquidityGrabMetadata,
    LiquidityGrabExecutionContext
)
from backend.liquidity_grab_engine.pipeline.pipeline import LiquidityGrabPipeline
from backend.liquidity_grab_engine.repository.memory import InMemoryLiquidityGrabRepository
from backend.liquidity_grab_engine.engine.engine import LiquidityGrabEngine

@pytest.mark.asyncio
async def test_engine_orchestration():
    pipeline = LiquidityGrabPipeline(stages=[])
    repo = InMemoryLiquidityGrabRepository()
    engine = LiquidityGrabEngine(pipeline=pipeline, repository=repo)
    
    config = LiquidityGrabConfiguration()
    meta = LiquidityGrabMetadata(
        execution_start_timestamp=datetime.now(timezone.utc),
        pipeline_version="1.0"
    )
    context = LiquidityGrabExecutionContext(
        symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")),
        timeframe=Timeframe.H1,
        dataset_version=1,
        parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1,
        configuration=config,
        metadata=meta
    )
    
    snapshot = await engine.execute(context)
    
    assert snapshot is not None
    assert snapshot.pipeline_version == "1.0"
    assert snapshot.parent_trend_snapshot_version == 1
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded == snapshot
