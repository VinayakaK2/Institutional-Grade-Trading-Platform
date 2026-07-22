import pytest
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposureExecutionContext, PortfolioExposurePipelineContext
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_state_engine.models.state import PortfolioState, OpenPosition, CapitalSummary
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_engine.models.references import ParentSnapshotReferences

from backend.portfolio_exposure_engine.pipeline.capital_exposure import CapitalExposureStage
from backend.portfolio_exposure_engine.pipeline.position_weight import PositionWeightStage
from backend.portfolio_exposure_engine.pipeline.sector_exposure import SectorExposureStage
from backend.portfolio_exposure_engine.pipeline.industry_exposure import IndustryExposureStage
from backend.portfolio_exposure_engine.pipeline.gross_net_exposure import GrossNetExposureStage
from backend.portfolio_exposure_engine.pipeline.metrics_assembly import MetricsAssemblyStage

from backend.portfolio_exposure_engine.rules.structural_rules import PortfolioExposureStructuralRules
from backend.portfolio_exposure_engine.rules.consistency_rules import PortfolioExposureConsistencyRules

from backend.portfolio_exposure_engine.repository.memory_repo import MemoryPortfolioExposureRepository
from backend.portfolio_exposure_engine.services.query_service import MemoryPortfolioExposureQueryService
from backend.portfolio_exposure_engine.builders.snapshot_builder import PortfolioExposureSnapshotBuilder

@pytest.fixture
def mock_state_snapshot():
    state = PortfolioState(
        positions=[
            OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0, sector="Technology", industry="Consumer Electronics"),
            OpenPosition(symbol="JPM", quantity=5, average_entry_price=100.0, current_price=110.0, sector="Financials", industry="Banking")
        ],
        capital=CapitalSummary(available_capital=10000.0, used_capital=2100.0, cash_balance=11500.0)
    )
    return PortfolioStateSnapshot(
        snapshot_id="test_state_1",
        portfolio_state=state,
        parent_snapshot_references=ParentSnapshotReferences(risk_snapshot_version="risk_1"),
        dataset_version="v1",
        pipeline_version="1.0",
        configuration_hash="abc"
    )

@pytest.fixture
def valid_context(mock_state_snapshot):
    return PortfolioExposureExecutionContext(
        portfolio_state_snapshot=mock_state_snapshot,
        configuration=PortfolioConfiguration()
    )

@pytest.fixture
def pipeline_context(valid_context):
    return PortfolioExposurePipelineContext(
        execution_context=valid_context,
        execution_id="123"
    )

def test_structural_rules(valid_context):
    rules = PortfolioExposureStructuralRules()
    assert rules.validate(valid_context).is_valid
    
def test_consistency_rules(valid_context):
    rules = PortfolioExposureConsistencyRules()
    assert rules.validate(valid_context).is_valid
    
    invalid = valid_context.portfolio_state_snapshot.model_copy(update={"dataset_version": ""})
    invalid_ctx = valid_context.model_copy(update={"portfolio_state_snapshot": invalid})
    assert not rules.validate(invalid_ctx).is_valid

@pytest.mark.asyncio
async def test_capital_exposure_stage(pipeline_context):
    stage = CapitalExposureStage()
    res = await stage.execute(pipeline_context)
    
    # AAPL = 10 * 155 = 1550, JPM = 5 * 110 = 550. Total invested = 2100
    # Available = 10000. Total value = 12100
    assert res.exposure_analysis.capital_exposure.total_invested_capital == 2100.0
    assert res.exposure_analysis.capital_exposure.available_capital == 10000.0
    assert round(res.exposure_analysis.capital_exposure.capital_utilization_percent, 2) == 17.36
    assert round(res.exposure_analysis.capital_exposure.cash_allocation, 2) == 82.64

@pytest.mark.asyncio
async def test_position_weight_stage(pipeline_context):
    # Needs capital exposure first
    ctx = await CapitalExposureStage().execute(pipeline_context)
    res = await PositionWeightStage().execute(ctx)
    
    weights = res.exposure_analysis.position_exposure.individual_weights
    # AAPL = 1550 / 12100 = 12.81%
    assert round(weights["AAPL"], 2) == 12.81
    assert round(weights["JPM"], 2) == 4.55
    assert res.exposure_analysis.position_exposure.largest_position == "AAPL"
    assert res.exposure_analysis.position_exposure.smallest_position == "JPM"

@pytest.mark.asyncio
async def test_sector_and_industry_stages(pipeline_context):
    ctx = await CapitalExposureStage().execute(pipeline_context)
    ctx = await PositionWeightStage().execute(ctx)
    
    sec_res = await SectorExposureStage().execute(ctx)
    assert sec_res.exposure_analysis.sector_exposure.exposure_per_sector["Technology"] == 1550.0
    assert round(sec_res.exposure_analysis.sector_exposure.sector_weights["Technology"], 2) == 12.81
    
    ind_res = await IndustryExposureStage().execute(sec_res)
    assert ind_res.exposure_analysis.industry_exposure.exposure_per_industry["Banking"] == 550.0

@pytest.mark.asyncio
async def test_gross_net_exposure_stage(pipeline_context):
    res = await GrossNetExposureStage().execute(pipeline_context)
    # Both long
    assert res.exposure_analysis.gross_net_exposure.long_exposure == 2100.0
    assert res.exposure_analysis.gross_net_exposure.short_exposure == 0.0
    assert res.exposure_analysis.gross_net_exposure.gross_exposure == 2100.0
    assert res.exposure_analysis.gross_net_exposure.net_exposure == 2100.0

@pytest.mark.asyncio
async def test_metrics_assembly_stage(pipeline_context):
    ctx = await CapitalExposureStage().execute(pipeline_context)
    ctx = await PositionWeightStage().execute(ctx)
    ctx = await SectorExposureStage().execute(ctx)
    ctx = await IndustryExposureStage().execute(ctx)
    ctx = await GrossNetExposureStage().execute(ctx)
    
    res = await MetricsAssemblyStage().execute(ctx)
    metrics = res.exposure_analysis.exposure_metrics
    assert metrics.total_positions == 2
    assert metrics.sector_count == 2
    assert metrics.industry_count == 2
    assert round(metrics.largest_position_weight, 2) == 12.81

@pytest.mark.asyncio
async def test_memory_repo_and_query_service():
    repo = MemoryPortfolioExposureRepository()
    query_svc = MemoryPortfolioExposureQueryService(repo)
    
    assert await query_svc.get_latest_exposure() is None
    assert await query_svc.get_history() == []
    assert await query_svc.query_by_symbol("AAPL") == []
    
    with pytest.raises(KeyError):
        await repo.load("nonexistent")
    
    assert await repo.exists("nonexistent") is False
    
def test_snapshot_builder_missing_fields():
    builder = PortfolioExposureSnapshotBuilder()
    with pytest.raises(ValueError, match="required"):
        builder.build()
