import pytest
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository
from backend.portfolio_optimization_engine.services.query_service import PortfolioOptimizationQueryService
from backend.portfolio_optimization_engine.core.engine import PortfolioOptimizationEngine

@pytest.fixture
def memory_repo():
    return MemoryPortfolioOptimizationRepository()

@pytest.fixture
def query_service(memory_repo):
    return PortfolioOptimizationQueryService(repository=memory_repo)

@pytest.fixture
def engine(memory_repo):
    return PortfolioOptimizationEngine(repository=memory_repo)

@pytest.mark.asyncio
async def test_repository_save_load(memory_repo, engine, mock_execution_context):
    snapshot = await engine.optimize(mock_execution_context)
    
    assert await memory_repo.exists(snapshot.snapshot_id)
    loaded = await memory_repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_repository_load_latest(memory_repo, engine, mock_execution_context):
    await engine.optimize(mock_execution_context)
    snapshot2 = await engine.optimize(mock_execution_context)
    
    latest = await memory_repo.load_latest()
    assert latest == snapshot2

@pytest.mark.asyncio
async def test_query_service_load_latest(query_service, engine, mock_execution_context):
    snapshot = await engine.optimize(mock_execution_context)
    
    latest = await query_service.load_latest()
    assert latest == snapshot

@pytest.mark.asyncio
async def test_query_service_not_implemented(query_service):
    with pytest.raises(NotImplementedError):
        await query_service.query_by_symbol("AAPL")
        
    with pytest.raises(NotImplementedError):
        await query_service.query_by_portfolio("port_1")
        
    with pytest.raises(NotImplementedError):
        await query_service.query_by_time_range("start", "end")
