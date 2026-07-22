import pytest
from backend.portfolio_engine.core.engine import PortfolioEngine
from backend.portfolio_engine.core.pipeline import PortfolioPipeline
from backend.portfolio_engine.models.context import PortfolioExecutionContext
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_engine.repository.memory_repo import MemoryPortfolioRepository
from backend.portfolio_engine.validation.structural import StructuralValidator
from backend.portfolio_engine.validation.consistency import ConsistencyValidator
from backend.portfolio_engine.exceptions import PortfolioEngineError, PortfolioRepositoryError

@pytest.fixture
def repo():
    return MemoryPortfolioRepository()

@pytest.fixture
def structural():
    return StructuralValidator()

@pytest.fixture
def consistency():
    return ConsistencyValidator()

@pytest.fixture
def pipeline():
    return PortfolioPipeline()

@pytest.fixture
def engine(repo, structural, consistency, pipeline):
    return PortfolioEngine(repo, structural, consistency, pipeline)

@pytest.fixture
def valid_context():
    return PortfolioExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version="v1.0",
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1.0"),
        configuration=PortfolioConfiguration()
    )

@pytest.mark.asyncio
async def test_successful_execution(engine, valid_context, repo):
    snapshot = await engine.execute(valid_context)
    
    assert snapshot is not None
    assert snapshot.snapshot_id.startswith("port_")
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded.snapshot_id == snapshot.snapshot_id
    assert loaded.dataset_version == "v1.0"

@pytest.mark.asyncio
async def test_validation_failure(engine, valid_context):
    invalid_context = valid_context.model_copy(update={"dataset_version": ""})
    with pytest.raises(PortfolioEngineError, match="Structural Validation Failed"):
        await engine.execute(invalid_context)

@pytest.mark.asyncio
async def test_duplicate_snapshot_repo_error(engine, valid_context, repo):
    snapshot1 = await engine.execute(valid_context)
    # Re-inserting the identical snapshot should fail
    with pytest.raises(PortfolioRepositoryError, match="already exists"):
        await repo.save(snapshot1)
