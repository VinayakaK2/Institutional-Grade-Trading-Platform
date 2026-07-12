import pytest
from backend.liquidity_grab_engine.quality.repository.postgres import PostgreSQLQualityRepository

@pytest.mark.asyncio
async def test_postgres_repository_unimplemented():
    repo = PostgreSQLQualityRepository()
    
    with pytest.raises(NotImplementedError):
        await repo.save(None)
        
    with pytest.raises(NotImplementedError):
        await repo.load("r1")
        
    with pytest.raises(NotImplementedError):
        await repo.exists("r1")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_candidate("c1")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_symbol("BTC")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_quality(None)
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_parent_trend_snapshot(1)
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_parent_consolidation_snapshot(1)
        
    with pytest.raises(NotImplementedError):
        await repo.load_latest()
