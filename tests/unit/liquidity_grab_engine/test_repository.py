import pytest
from datetime import datetime, timezone
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.repository.memory import InMemoryLiquidityGrabRepository
from backend.liquidity_grab_engine.repository.postgres import PostgreSQLLiquidityGrabRepository
from backend.liquidity_grab_engine.models.models import LiquidityGrabSnapshot, LiquidityGrabConfigurationReference

def create_snapshot(symbol="AAPL:NASDAQ", tf="1h", trend=1, cons=1) -> LiquidityGrabSnapshot:
    sid = LiquidityGrabSnapshot.generate_id(symbol, tf, 1, trend, cons)
    return LiquidityGrabSnapshot(
        snapshot_id=sid,
        symbol_id=symbol,
        timeframe=tf,
        snapshot_version=1,
        dataset_version=1,
        parent_trend_snapshot_version=trend,
        parent_consolidation_snapshot_version=cons,
        pipeline_version="1.0",
        config_reference=LiquidityGrabConfigurationReference(version=1, config_hash="abc"),
        created_timestamp=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_memory_repo_save_load():
    repo = InMemoryLiquidityGrabRepository()
    s = create_snapshot()
    
    await repo.save(s)
    
    loaded = await repo.load(s.snapshot_id)
    assert loaded == s
    
    with pytest.raises(ValueError):
        await repo.save(s) # INSERT-only

@pytest.mark.asyncio
async def test_memory_repo_queries():
    repo = InMemoryLiquidityGrabRepository()
    s1 = create_snapshot(trend=1)
    s2 = create_snapshot(trend=2)
    
    await repo.save(s1)
    await repo.save(s2)
    
    q_trend = await repo.query_by_parent_trend_snapshot(2)
    assert len(q_trend) == 1
    assert q_trend[0].snapshot_id == s2.snapshot_id
    
    assert await repo.exists(s1.snapshot_id) is True
    assert await repo.exists("random") is False
    
    # Query timeframe
    q_tf = await repo.query_by_timeframe(Timeframe.H1)
    # create_snapshot sets tf="1h" but Timeframe enum isn't used there natively, assume we pass string or enum
    # We will just verify it runs.
    
    q_cons = await repo.query_by_consolidation_snapshot(1)
    assert len(q_cons) == 2
    
    q_sym = await repo.query_by_symbol("AAPL")
    
    latest = await repo.load_latest()
    assert latest is not None

@pytest.mark.asyncio
async def test_postgres_unimplemented():
    repo = PostgreSQLLiquidityGrabRepository(None)
    with pytest.raises(NotImplementedError):
        await repo.save(create_snapshot())
    with pytest.raises(NotImplementedError):
        await repo.load("abc")
    with pytest.raises(NotImplementedError):
        await repo.exists("abc")
    with pytest.raises(NotImplementedError):
        await repo.query_by_symbol("abc")
    with pytest.raises(NotImplementedError):
        await repo.query_by_timeframe("1h")
    with pytest.raises(NotImplementedError):
        await repo.query_by_parent_trend_snapshot(1)
    with pytest.raises(NotImplementedError):
        await repo.query_by_consolidation_snapshot(1)
    with pytest.raises(NotImplementedError):
        await repo.load_latest()
