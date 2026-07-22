import pytest
from backend.portfolio_state_engine.core.engine import PortfolioStateEngine
from backend.portfolio_state_engine.pipeline.pipeline import PortfolioStatePipeline
from backend.portfolio_state_engine.pipeline.position_assembly import PositionAssemblyStage
from backend.portfolio_state_engine.pipeline.pending_order_assembly import PendingOrderAssemblyStage
from backend.portfolio_state_engine.pipeline.capital_assembly import CapitalAssemblyStage
from backend.portfolio_state_engine.pipeline.pnl_assembly import PnLAssemblyStage
from backend.portfolio_state_engine.pipeline.snapshot_assembly import SnapshotAssemblyStage
from backend.portfolio_state_engine.models.context import PortfolioStateExecutionContext
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences
from backend.portfolio_state_engine.models.state import OpenPosition, CapitalSummary
from backend.portfolio_state_engine.repository.memory_repo import MemoryPortfolioStateRepository
from backend.portfolio_state_engine.rules.structural_rules import PortfolioStateStructuralRules
from backend.portfolio_state_engine.rules.consistency_rules import PortfolioStateConsistencyRules
from backend.portfolio_state_engine.exceptions import PortfolioStateValidationError, PortfolioStateRepositoryError

@pytest.fixture
def repo():
    return MemoryPortfolioStateRepository()

@pytest.fixture
def structural():
    return PortfolioStateStructuralRules()

@pytest.fixture
def consistency():
    return PortfolioStateConsistencyRules()

@pytest.fixture
def pipeline():
    return PortfolioStatePipeline(stages=[
        PositionAssemblyStage(),
        PendingOrderAssemblyStage(),
        CapitalAssemblyStage(),
        PnLAssemblyStage(),
        SnapshotAssemblyStage()
    ])

@pytest.fixture
def engine(repo, structural, consistency, pipeline):
    return PortfolioStateEngine(repo, structural, consistency, pipeline)

@pytest.fixture
def valid_context():
    return PortfolioStateExecutionContext(
        positions=[
            OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0)
        ],
        pending_orders=[],
        capital=CapitalSummary(available_capital=10000.0, used_capital=1500.0, cash_balance=11500.0),
        realized_pnl=50.0,
        unrealized_pnl=50.0,
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1.0"),
        dataset_version="v1.0",
        configuration=PortfolioConfiguration()
    )

@pytest.mark.asyncio
async def test_successful_execution(engine, valid_context, repo):
    snapshot = await engine.execute(valid_context)
    
    assert snapshot is not None
    assert snapshot.snapshot_id.startswith("port_state_")
    assert len(snapshot.portfolio_state.positions) == 1
    assert snapshot.portfolio_state.capital.available_capital == 10000.0
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded.snapshot_id == snapshot.snapshot_id
    assert loaded.dataset_version == "v1.0"

@pytest.mark.asyncio
async def test_validation_failure(engine, valid_context):
    invalid_context = valid_context.model_copy(update={"dataset_version": ""})
    with pytest.raises(PortfolioStateValidationError, match="Structural Validation Failed"):
        await engine.execute(invalid_context)

@pytest.mark.asyncio
async def test_duplicate_snapshot_repo_error(engine, valid_context, repo):
    snapshot1 = await engine.execute(valid_context)
    with pytest.raises(PortfolioStateRepositoryError, match="already exists"):
        await repo.save(snapshot1)
