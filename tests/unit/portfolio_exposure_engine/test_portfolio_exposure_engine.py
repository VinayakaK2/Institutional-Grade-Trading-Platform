import pytest
from backend.portfolio_exposure_engine.core.engine import PortfolioExposureEngine
from backend.portfolio_exposure_engine.pipeline.pipeline import PortfolioExposurePipeline, PortfolioExposurePipelineError
from backend.portfolio_exposure_engine.pipeline.capital_exposure import CapitalExposureStage
from backend.portfolio_exposure_engine.pipeline.position_weight import PositionWeightStage
from backend.portfolio_exposure_engine.pipeline.sector_exposure import SectorExposureStage
from backend.portfolio_exposure_engine.pipeline.industry_exposure import IndustryExposureStage
from backend.portfolio_exposure_engine.pipeline.gross_net_exposure import GrossNetExposureStage
from backend.portfolio_exposure_engine.pipeline.metrics_assembly import MetricsAssemblyStage

from backend.portfolio_exposure_engine.models.contexts import PortfolioExposureExecutionContext, PortfolioExposurePipelineContext
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_state_engine.models.state import PortfolioState, OpenPosition, CapitalSummary
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences

from backend.portfolio_exposure_engine.rules.structural_rules import PortfolioExposureStructuralRules
from backend.portfolio_exposure_engine.rules.consistency_rules import PortfolioExposureConsistencyRules
from backend.portfolio_exposure_engine.repository.memory_repo import MemoryPortfolioExposureRepository
from backend.portfolio_exposure_engine.exceptions import PortfolioExposureValidationError, PortfolioExposureRepositoryError

@pytest.fixture
def repo():
    return MemoryPortfolioExposureRepository()

@pytest.fixture
def structural():
    return PortfolioExposureStructuralRules()

@pytest.fixture
def consistency():
    return PortfolioExposureConsistencyRules()

@pytest.fixture
def pipeline():
    return PortfolioExposurePipeline(stages=[
        CapitalExposureStage(),
        PositionWeightStage(),
        SectorExposureStage(),
        IndustryExposureStage(),
        GrossNetExposureStage(),
        MetricsAssemblyStage()
    ])

@pytest.fixture
def engine(repo, structural, consistency, pipeline):
    return PortfolioExposureEngine(repo, structural, consistency, pipeline)

@pytest.fixture
def valid_context():
    state = PortfolioState(
        positions=[
            OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0, sector="Technology", industry="Consumer Electronics")
        ],
        capital=CapitalSummary(available_capital=10000.0, used_capital=1500.0, cash_balance=11500.0)
    )
    snap = PortfolioStateSnapshot(
        snapshot_id="test_state_1",
        portfolio_state=state,
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1"),
        dataset_version="v1.0",
        pipeline_version="1.0",
        configuration_hash="abc"
    )
    return PortfolioExposureExecutionContext(
        portfolio_state_snapshot=snap,
        configuration=PortfolioConfiguration()
    )

@pytest.mark.asyncio
async def test_successful_execution(engine, valid_context, repo):
    snapshot = await engine.execute(valid_context)
    
    assert snapshot is not None
    assert snapshot.snapshot_id.startswith("port_exp_")
    
    analysis = snapshot.exposure_analysis
    assert analysis.exposure_metrics.total_positions == 1
    assert "AAPL" in analysis.position_exposure.individual_weights
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded.snapshot_id == snapshot.snapshot_id

@pytest.mark.asyncio
async def test_validation_failure(engine, valid_context):
    invalid = valid_context.portfolio_state_snapshot.model_copy(update={"dataset_version": ""})
    invalid_ctx = valid_context.model_copy(update={"portfolio_state_snapshot": invalid})
    with pytest.raises(PortfolioExposureValidationError, match="Consistency Validation Failed"):
        await engine.execute(invalid_ctx)

@pytest.mark.asyncio
async def test_duplicate_snapshot_repo_error(engine, valid_context, repo):
    snapshot1 = await engine.execute(valid_context)
    with pytest.raises(PortfolioExposureRepositoryError, match="already exists"):
        await repo.save(snapshot1)
        
@pytest.mark.asyncio
async def test_pipeline_error_handling(valid_context):
    class FailingStage:
        async def execute(self, ctx):
            raise ValueError("Some random error")
            
    pipeline = PortfolioExposurePipeline([FailingStage()])
    pipeline_ctx = PortfolioExposurePipelineContext(
        execution_context=valid_context,
        execution_id="123"
    )
    
    with pytest.raises(PortfolioExposurePipelineError, match="Pipeline execution failed: Some random error"):
        await pipeline.execute(pipeline_ctx)

@pytest.mark.asyncio
async def test_query_service_by_symbol(engine, valid_context, repo):
    from backend.portfolio_exposure_engine.services.query_service import MemoryPortfolioExposureQueryService
    query_svc = MemoryPortfolioExposureQueryService(repo)
    
    # Save a snapshot
    await engine.execute(valid_context)
    
    # Should find AAPL
    results = await query_svc.query_by_symbol("AAPL")
    assert len(results) == 1
    
    # Should not find MSFT
    results = await query_svc.query_by_symbol("MSFT")
    assert len(results) == 0
