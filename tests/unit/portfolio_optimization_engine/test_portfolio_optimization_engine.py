import pytest
from backend.portfolio_optimization_engine.core.engine import PortfolioOptimizationEngine
from backend.portfolio_optimization_engine.repository.memory_repo import MemoryPortfolioOptimizationRepository

@pytest.fixture
def memory_repo():
    return MemoryPortfolioOptimizationRepository()

@pytest.fixture
def engine(memory_repo):
    return PortfolioOptimizationEngine(repository=memory_repo)

@pytest.mark.asyncio
async def test_engine_successful_optimization(engine, mock_execution_context, memory_repo):
    snapshot = await engine.optimize(mock_execution_context)
    
    assert snapshot is not None
    assert snapshot.optimization_result is not None
    assert snapshot.business_fingerprint is not None
    
    # Verify persistence
    saved = await memory_repo.load(snapshot.snapshot_id)
    assert saved == snapshot

@pytest.mark.asyncio
async def test_engine_determinism(engine, mock_execution_context):
    """
    Test that the snapshot generation process is strictly deterministic.
    Given the identical execution context, the generated business_fingerprint 
    must be identical across multiple runs.
    """
    snapshot_1 = await engine.optimize(mock_execution_context)
    snapshot_2 = await engine.optimize(mock_execution_context)
    
    # Different snapshot IDs due to random uuid
    assert snapshot_1.snapshot_id != snapshot_2.snapshot_id
    # Same business fingerprint
    assert snapshot_1.business_fingerprint == snapshot_2.business_fingerprint

@pytest.mark.asyncio
async def test_engine_fails_validation(engine, mock_execution_context):
    mock_execution_context.portfolio_state_snapshot = None
    with pytest.raises(ValueError):
        await engine.optimize(mock_execution_context)
