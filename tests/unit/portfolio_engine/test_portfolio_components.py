import pytest
from backend.portfolio_engine.models.context import PortfolioExecutionContext
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_engine.validation.structural import StructuralValidator
from backend.portfolio_engine.validation.consistency import ConsistencyValidator
from backend.portfolio_engine.repository.memory_repo import MemoryPortfolioRepository
from backend.portfolio_engine.services.query_service import MemoryQueryService
from backend.portfolio_engine.builders.snapshot_builder import PortfolioSnapshotBuilder

@pytest.fixture
def valid_context():
    return PortfolioExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1.0"),
        configuration=PortfolioConfiguration()
    )

def test_structural_validation(valid_context):
    validator = StructuralValidator()
    
    assert validator.validate(valid_context).is_valid
    assert not validator.validate(valid_context.model_copy(update={"symbol": ""})).is_valid
    assert not validator.validate(valid_context.model_copy(update={"timeframe": ""})).is_valid
    assert not validator.validate(valid_context.model_copy(update={"dataset_version": ""})).is_valid
    
    bad_refs = ParentSnapshotReferences(risk_snapshot_version="")
    assert not validator.validate(valid_context.model_copy(update={"parent_snapshot_references": bad_refs})).is_valid

def test_consistency_validation(valid_context):
    validator = ConsistencyValidator()
    
    assert validator.validate(valid_context).is_valid
    assert not validator.validate(valid_context.model_copy(update={"dataset_version": "1.0"})).is_valid

@pytest.mark.asyncio
async def test_repository_load_and_exists():
    repo = MemoryPortfolioRepository()
    refs = ParentSnapshotReferences(risk_snapshot_version="v1.0")
    s1 = PortfolioSnapshotBuilder() \
        .with_dataset_version("v1.0") \
        .with_parent_snapshot_references(refs) \
        .with_configuration_hash("hash") \
        .with_metadata({"symbol": "AAPL", "timeframe": "1D"}) \
        .build()
        
    await repo.save(s1)
    assert await repo.exists(s1.snapshot_id)
    assert not await repo.exists("missing")
    
    loaded = await repo.load(s1.snapshot_id)
    assert loaded.snapshot_id == s1.snapshot_id
    
    with pytest.raises(KeyError):
        await repo.load("missing")

@pytest.mark.asyncio
async def test_query_service():
    repo = MemoryPortfolioRepository()
    qs = MemoryQueryService(repo)
    
    refs = ParentSnapshotReferences(risk_snapshot_version="risk_1.0")
    s1 = PortfolioSnapshotBuilder() \
        .with_dataset_version("v1.0") \
        .with_parent_snapshot_references(refs) \
        .with_configuration_hash("hash") \
        .with_metadata({"symbol": "AAPL", "timeframe": "1D"}) \
        .build()
        
    await repo.save(s1)
    
    latest = await qs.load_latest_snapshot("AAPL", "1D")
    assert latest.snapshot_id == s1.snapshot_id
    
    missing = await qs.load_latest_snapshot("MSFT", "1D")
    assert missing is None
    
    lineage = await qs.load_snapshot_lineage("risk_1.0")
    assert len(lineage) == 1
    
    empty_lineage = await qs.load_snapshot_lineage("missing")
    assert len(empty_lineage) == 0
