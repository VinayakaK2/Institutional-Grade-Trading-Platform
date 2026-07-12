import pytest
from backend.liquidity_grab_engine.lifecycle.repository.postgres import PostgreSQLLifecycleRepository
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleState

@pytest.mark.asyncio
async def test_postgres_repository_unimplemented():
    repo = PostgreSQLLifecycleRepository()
    
    with pytest.raises(NotImplementedError):
        await repo.save(None)
        
    with pytest.raises(NotImplementedError):
        await repo.load("id")
        
    with pytest.raises(NotImplementedError):
        await repo.exists("id")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_candidate("c")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_symbol("s")
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_state(LiquidityGrabLifecycleState.ACTIVE)
        
    with pytest.raises(NotImplementedError):
        await repo.query_by_quality_report("q")
        
    with pytest.raises(NotImplementedError):
        await repo.load_latest("c")
