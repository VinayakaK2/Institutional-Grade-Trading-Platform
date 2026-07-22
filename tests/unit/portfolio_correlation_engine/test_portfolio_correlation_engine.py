import pytest
from backend.portfolio_correlation_engine.core.engine import PortfolioCorrelationEngine
from backend.portfolio_correlation_engine.repository.memory_repo import MemoryPortfolioCorrelationRepository
from backend.portfolio_correlation_engine.rules.structural_rules import PortfolioCorrelationStructuralRules
from backend.portfolio_correlation_engine.rules.consistency_rules import PortfolioCorrelationConsistencyRules
from backend.portfolio_correlation_engine.pipeline.pipeline import PortfolioCorrelationPipeline
from backend.portfolio_correlation_engine.pipeline.symbol_correlation import SymbolCorrelationStage
from backend.portfolio_correlation_engine.pipeline.sector_correlation import SectorCorrelationStage
from backend.portfolio_correlation_engine.pipeline.industry_correlation import IndustryCorrelationStage
from backend.portfolio_correlation_engine.pipeline.strategy_correlation import StrategyCorrelationStage
from backend.portfolio_correlation_engine.pipeline.directional_correlation import DirectionalCorrelationStage
from backend.portfolio_correlation_engine.pipeline.metrics_assembly import MetricsAssemblyStage
from backend.portfolio_correlation_engine.exceptions import PortfolioCorrelationValidationError, PortfolioCorrelationRepositoryError
from tests.unit.portfolio_correlation_engine.test_portfolio_correlation_components import valid_context, mock_state, mock_exposure, mock_candidate, mock_risk

@pytest.fixture
def repo():
    return MemoryPortfolioCorrelationRepository()

@pytest.fixture
def engine(repo):
    stages = [
        SymbolCorrelationStage(),
        SectorCorrelationStage(),
        IndustryCorrelationStage(),
        StrategyCorrelationStage(),
        DirectionalCorrelationStage(),
        MetricsAssemblyStage()
    ]
    pipeline = PortfolioCorrelationPipeline(stages)
    return PortfolioCorrelationEngine(
        repository=repo,
        structural_rules=PortfolioCorrelationStructuralRules(),
        consistency_rules=PortfolioCorrelationConsistencyRules(),
        pipeline=pipeline
    )

@pytest.mark.asyncio
async def test_engine_execution_success(engine, valid_context, repo):
    snapshot = await engine.execute(valid_context)
    
    assert snapshot.snapshot_id.startswith("port_corr_")
    assert snapshot.dataset_version == "v1"
    assert "execution_id" in snapshot.metadata
    assert "SymbolCorrelationStage" in snapshot.metadata["stage_timings"]
    
    # Check Repo
    stored = await repo.load(snapshot.snapshot_id)
    assert stored.snapshot_id == snapshot.snapshot_id

@pytest.mark.asyncio
async def test_engine_structural_failure(engine, valid_context):
    invalid_context = valid_context.model_copy(update={"candidate_position_snapshot": None})
    with pytest.raises(PortfolioCorrelationValidationError, match="Structural Validation Failed"):
        await engine.execute(invalid_context)
        
@pytest.mark.asyncio
async def test_engine_consistency_failure(engine, valid_context):
    invalid_candidate = valid_context.candidate_position_snapshot.model_copy(update={"dataset_version": "v99"})
    invalid_context = valid_context.model_copy(update={"candidate_position_snapshot": invalid_candidate})
    with pytest.raises(PortfolioCorrelationValidationError, match="Consistency Validation Failed"):
        await engine.execute(invalid_context)
        
@pytest.mark.asyncio
async def test_repo_update_forbidden(repo, engine, valid_context):
    snapshot = await engine.execute(valid_context)
    with pytest.raises(PortfolioCorrelationRepositoryError, match="Updates are strictly forbidden"):
        await repo.save(snapshot)

@pytest.mark.asyncio
async def test_pipeline_failure(repo, valid_context):
    class FailingStage:
        async def execute(self, context):
            raise ValueError("Some internal error")
            
    pipeline = PortfolioCorrelationPipeline([FailingStage()])
    engine = PortfolioCorrelationEngine(
        repository=repo,
        structural_rules=PortfolioCorrelationStructuralRules(),
        consistency_rules=PortfolioCorrelationConsistencyRules(),
        pipeline=pipeline
    )
    
    from backend.portfolio_correlation_engine.exceptions import PortfolioCorrelationPipelineError
    with pytest.raises(PortfolioCorrelationPipelineError, match="Pipeline execution failed"):
        await engine.execute(valid_context)
