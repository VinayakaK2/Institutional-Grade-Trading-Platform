import pytest
from backend.portfolio_correlation_engine.repository.memory_repo import MemoryPortfolioCorrelationRepository
from backend.portfolio_correlation_engine.services.query_service import MemoryPortfolioCorrelationQueryService
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot
from backend.portfolio_correlation_engine.models.correlation_models import PortfolioCorrelationAnalysis, CorrelationMetrics
from backend.portfolio_correlation_engine.models.references import ParentSnapshotReferences, SnapshotReference
from datetime import datetime, timezone

@pytest.fixture
def repo():
    return MemoryPortfolioCorrelationRepository()
    
@pytest.fixture
def query_service(repo):
    return MemoryPortfolioCorrelationQueryService(repo)

@pytest.fixture
def mock_snapshot_base():
    analysis = PortfolioCorrelationAnalysis()
    metrics = CorrelationMetrics()
    refs = ParentSnapshotReferences(
        portfolio_state_snapshot=SnapshotReference(snapshot_id="s1"),
        portfolio_exposure_snapshot=SnapshotReference(snapshot_id="e1"),
        candidate_position_snapshot=SnapshotReference(snapshot_id="c1"),
        risk_decision_snapshot=SnapshotReference(snapshot_id="r1")
    )
    def _create(snap_id: str, candidate_symbol: str):
        return PortfolioCorrelationSnapshot(
            snapshot_id=snap_id,
            schema_version="1.0",
            correlation_analysis=analysis,
            correlation_metrics=metrics,
            parent_snapshot_references=refs,
            configuration_snapshot_id="cfg1",
            dataset_version="v1",
            metadata={"candidate_symbol": candidate_symbol},
            created_at=datetime.now(timezone.utc)
        )
    return _create

@pytest.mark.asyncio
async def test_repository_load_not_found(repo):
    with pytest.raises(KeyError):
        await repo.load("missing")

@pytest.mark.asyncio
async def test_repository_exists(repo, mock_snapshot_base):
    snap = mock_snapshot_base("snap1", "AAPL")
    await repo.save(snap)
    
    assert await repo.exists("snap1") is True
    assert await repo.exists("snap2") is False

@pytest.mark.asyncio
async def test_query_service_get_latest_none(query_service):
    res = await query_service.get_latest_correlation()
    assert res is None

@pytest.mark.asyncio
async def test_query_service_history_and_latest(repo, query_service, mock_snapshot_base):
    snap1 = mock_snapshot_base("snap1", "AAPL")
    snap2 = mock_snapshot_base("snap2", "MSFT")
    
    await repo.save(snap1)
    # small delay to ensure created_at differs if we relied on that, 
    # but here created_at is captured on instantiation which is fine.
    await repo.save(snap2)
    
    history = await query_service.get_history()
    assert len(history) == 2
    
    latest = await query_service.get_latest_correlation()
    assert latest.snapshot_id in ["snap1", "snap2"]
    
@pytest.mark.asyncio
async def test_query_service_by_symbol(repo, query_service, mock_snapshot_base):
    snap1 = mock_snapshot_base("snap1", "AAPL")
    snap2 = mock_snapshot_base("snap2", "MSFT")
    snap3 = mock_snapshot_base("snap3", "AAPL")
    
    await repo.save(snap1)
    await repo.save(snap2)
    await repo.save(snap3)
    
    aapl_corrs = await query_service.query_by_symbol("AAPL")
    assert len(aapl_corrs) == 2
    assert all(s.metadata.get("candidate_symbol") == "AAPL" for s in aapl_corrs)
    
    msft_corrs = await query_service.query_by_symbol("MSFT")
    assert len(msft_corrs) == 1
    assert msft_corrs[0].snapshot_id == "snap2"
