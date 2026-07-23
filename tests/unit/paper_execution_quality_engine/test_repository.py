import pytest
from backend.paper_execution_quality_engine.repository.memory_repo import MemoryPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.repository.postgres_repo import PostgreSQLPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.services.query_service import PaperExecutionQualityQueryService
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_quality_engine.models.execution_quality import (
    ExecutionQualityReport, MarketImpactMetrics, SlippageMetrics, SpreadMetrics, GapMetrics, LiquidityMetrics
)
from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityPersistenceError

@pytest.fixture
def dummy_snapshot():
    report = ExecutionQualityReport(
        market_impact=MarketImpactMetrics(expected_execution_price=0.0, market_impact=0.0, impact_percentage=0.0, impact_cost=0.0),
        slippage=SlippageMetrics(expected_price=0.0, actual_fill_price=0.0, slippage_amount=0.0, slippage_percentage=0.0),
        spread_cost=SpreadMetrics(bid_price=0.0, ask_price=0.0, mid_price=0.0, effective_spread=0.0, paid_spread=0.0),
        gap_cost=GapMetrics(gap_up=False, gap_down=False, gap_size=0.0, gap_impact=0.0),
        liquidity_metrics=LiquidityMetrics(available_liquidity=0.0, executed_quantity=0.0, remaining_liquidity=0.0, liquidity_utilization=0.0)
    )
    return PaperExecutionQualitySnapshot(
        snapshot_id="snap1",
        schema_version="13.4.0",
        dataset_version="v1",
        snapshot_version="snap1",
        parent_fill_snapshot_version="fill1",
        execution_quality_report=report,
        business_fingerprint="fingerprint1",
        snapshot_hash="hash1",
        created_at="2026-07-22T00:00:00Z",
        metadata={}
    )

def test_memory_repo(dummy_snapshot):
    repo = MemoryPaperExecutionQualityRepository()
    repo.save(dummy_snapshot)
    assert repo.exists("snap1")
    assert repo.load("snap1") == dummy_snapshot
    assert repo.load_latest() == dummy_snapshot
    
    with pytest.raises(PaperExecutionQualityPersistenceError):
        repo.save(dummy_snapshot)

def test_query_service(dummy_snapshot):
    repo = MemoryPaperExecutionQualityRepository()
    repo.save(dummy_snapshot)
    service = PaperExecutionQualityQueryService(repository=repo)
    
    results = service.query_by_parent_fill_snapshot("fill1")
    assert len(results) == 1
    assert results[0].snapshot_version == "snap1"

def test_memory_repo_empty():
    repo = MemoryPaperExecutionQualityRepository()
    assert repo.load_latest() is None
    assert repo.load("snap1") is None
    assert not repo.exists("snap1")
    assert repo.query_by_parent_fill_snapshot("fill1") == []

def test_postgres_repo():
    repo = PostgreSQLPaperExecutionQualityRepository()
    with pytest.raises(NotImplementedError):
        repo.save(None)
    with pytest.raises(NotImplementedError):
        repo.load("snap1")
    with pytest.raises(NotImplementedError):
        repo.exists("snap1")
    with pytest.raises(NotImplementedError):
        repo.load_latest()
    with pytest.raises(NotImplementedError):
        repo.query_by_parent_fill_snapshot("fill1")
