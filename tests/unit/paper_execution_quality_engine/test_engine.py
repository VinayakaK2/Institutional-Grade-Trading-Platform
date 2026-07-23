import pytest
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, ParentSnapshotReferences
from backend.paper_execution_quality_engine.core.engine import PaperExecutionQualityEngine
from backend.paper_execution_quality_engine.repository.memory_repo import MemoryPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.validation.consistency import ConsistencyValidator
from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityValidationError

@pytest.fixture
def repo():
    return MemoryPaperExecutionQualityRepository()

@pytest.fixture
def consistency():
    return ConsistencyValidator()

@pytest.fixture
def engine(repo, consistency):
    return PaperExecutionQualityEngine(repository=repo, consistency_validator=consistency)

@pytest.mark.asyncio
async def test_engine_flow_success(engine, repo):
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={
            "market_impact": {"expected_execution_price": 50000, "impact_percentage": 0.0},
            "slippage": {"expected_price": 50000, "actual_fill_price": 50000},
            "spread": {"bid_price": 49900, "ask_price": 50100},
            "gap": {"gap_up": False, "gap_down": False},
            "liquidity": {"available_liquidity": 100.0, "executed_quantity": 25.0}
        }
    )
    
    snapshot = await engine.execute(ctx)
    
    assert snapshot is not None
    assert snapshot.parent_fill_snapshot_version == "fill_v1"
    assert repo.exists(snapshot.snapshot_version)
    assert repo.load_latest() == snapshot

@pytest.mark.asyncio
async def test_engine_structural_failure(engine):
    # Missing symbol
    ctx = PaperExecutionQualityExecutionContext(
        symbol="", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={}
    )
    
    with pytest.raises(PaperExecutionQualityValidationError):
        await engine.execute(ctx)
