import pytest
from unittest.mock import AsyncMock

from backend.consolidation_engine.optimization.services import ConsolidationOptimizationQueryService
from backend.consolidation_engine.optimization.repository.memory import InMemoryConsolidationOptimizationRepository
from backend.consolidation_engine.optimization.models import (
    ConsolidationOptimizationSnapshot,
    OptimizationBusinessStatistics,
    OptimizationRuntimeStatistics
)

@pytest.fixture
def repo():
    r = InMemoryConsolidationOptimizationRepository()
    r.load_latest = AsyncMock()
    r.query_by_parent = AsyncMock()
    r.load_by_fingerprint = AsyncMock()
    return r
    
@pytest.fixture
def service(repo):
    return ConsolidationOptimizationQueryService(repo)
    
@pytest.mark.asyncio
async def test_latest_optimization_snapshot(service, repo):
    await service.latest_optimization_snapshot()
    repo.load_latest.assert_called_once()
    
@pytest.mark.asyncio
async def test_historical_optimization_snapshots(service, repo):
    await service.historical_optimization_snapshots("parent1")
    repo.query_by_parent.assert_called_once_with("parent1")
    
@pytest.mark.asyncio
async def test_fingerprint_lookup(service, repo):
    await service.fingerprint_lookup("finger1")
    repo.load_by_fingerprint.assert_called_once_with("finger1")
    
@pytest.mark.asyncio
async def test_latest_statistics(service, repo):
    mock_snapshot = AsyncMock(spec=ConsolidationOptimizationSnapshot)
    mock_snapshot.business_statistics = OptimizationBusinessStatistics()
    mock_snapshot.runtime_statistics = OptimizationRuntimeStatistics()
    
    repo.load_latest.return_value = mock_snapshot
    
    biz = await service.latest_business_statistics()
    run = await service.latest_runtime_statistics()
    
    assert biz is not None
    assert run is not None
