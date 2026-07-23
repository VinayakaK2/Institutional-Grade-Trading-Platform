import pytest
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, ParentSnapshotReferences
from backend.paper_execution_quality_engine.core.engine import PaperExecutionQualityEngine
from backend.paper_execution_quality_engine.repository.memory_repo import MemoryPaperExecutionQualityRepository
from backend.paper_execution_quality_engine.validation.consistency import ConsistencyValidator

@pytest.fixture
def base_context():
    return PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={
            "market_impact": {"expected_execution_price": 50000, "impact_percentage": 1.0},
            "slippage": {"expected_price": 50000, "actual_fill_price": 50050},
            "spread": {"bid_price": 49950, "ask_price": 50050},
            "gap": {"gap_up": True, "gap_down": False, "gap_size": 100, "gap_impact": 50},
            "liquidity": {"available_liquidity": 1000.0, "executed_quantity": 250.0}
        }
    )

@pytest.mark.asyncio
async def test_replay_determinism(base_context):
    repo1 = MemoryPaperExecutionQualityRepository()
    engine1 = PaperExecutionQualityEngine(repo1, ConsistencyValidator())
    snapshot1 = await engine1.execute(base_context)
    
    repo2 = MemoryPaperExecutionQualityRepository()
    engine2 = PaperExecutionQualityEngine(repo2, ConsistencyValidator())
    snapshot2 = await engine2.execute(base_context)
    
    assert snapshot1.business_fingerprint == snapshot2.business_fingerprint
    assert snapshot1.snapshot_hash == snapshot2.snapshot_hash
    assert snapshot1.execution_quality_report == snapshot2.execution_quality_report
    
    # Asserting that only snapshot version and creation time change
    assert snapshot1.snapshot_version != snapshot2.snapshot_version
    
@pytest.mark.asyncio
async def test_snapshot_immutability(base_context):
    repo = MemoryPaperExecutionQualityRepository()
    engine = PaperExecutionQualityEngine(repo, ConsistencyValidator())
    snapshot = await engine.execute(base_context)
    
    # Repository load should not mutate state
    loaded_snapshot = repo.load(snapshot.snapshot_version)
    
    assert snapshot.business_fingerprint == loaded_snapshot.business_fingerprint
    assert snapshot.snapshot_hash == loaded_snapshot.snapshot_hash
    assert snapshot.execution_quality_report == loaded_snapshot.execution_quality_report
