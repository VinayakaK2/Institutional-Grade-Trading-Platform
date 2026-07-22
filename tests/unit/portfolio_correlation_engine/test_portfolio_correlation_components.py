import pytest
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationExecutionContext, PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.candidate import CandidatePositionSnapshot
from backend.portfolio_correlation_engine.models.configuration import PortfolioCorrelationConfigurationSnapshot
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_state_engine.models.state import PortfolioState, OpenPosition, CapitalSummary
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_exposure_engine.models.exposure_models import PortfolioExposureAnalysis, GrossNetExposure, SectorExposure, IndustryExposure
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.portfolio_engine.models.references import ParentSnapshotReferences as StateParentRefs
from unittest.mock import MagicMock
from backend.portfolio_correlation_engine.pipeline.symbol_correlation import SymbolCorrelationStage
from backend.portfolio_correlation_engine.pipeline.sector_correlation import SectorCorrelationStage
from backend.portfolio_correlation_engine.pipeline.industry_correlation import IndustryCorrelationStage
from backend.portfolio_correlation_engine.pipeline.strategy_correlation import StrategyCorrelationStage
from backend.portfolio_correlation_engine.pipeline.directional_correlation import DirectionalCorrelationStage
from backend.portfolio_correlation_engine.pipeline.metrics_assembly import MetricsAssemblyStage

from backend.portfolio_correlation_engine.rules.structural_rules import PortfolioCorrelationStructuralRules
from backend.portfolio_correlation_engine.rules.consistency_rules import PortfolioCorrelationConsistencyRules
from backend.portfolio_correlation_engine.builders.snapshot_builder import PortfolioCorrelationSnapshotBuilder

@pytest.fixture
def mock_candidate():
    return CandidatePositionSnapshot(
        snapshot_id="cand_1",
        symbol="AAPL",
        instrument="Stock",
        exchange="NASDAQ",
        asset_class="Equity",
        sector="Technology",
        industry="Consumer Electronics",
        strategy_identifier="Momentum",
        direction="Long",
        entry_type="Market",
        signal_identifier="sig_1",
        trade_identifier="trd_1",
        dataset_version="v1",
        configuration_version="1.0",
        business_fingerprint="bf_cand_1"
    )

@pytest.fixture
def mock_state():
    state = PortfolioState(
        positions=[
            OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0, sector="Technology", industry="Consumer Electronics"),
            OpenPosition(symbol="JPM", quantity=5, average_entry_price=100.0, current_price=110.0, sector="Financials", industry="Banking")
        ],
        capital=CapitalSummary(available_capital=10000.0, used_capital=2100.0, cash_balance=11500.0)
    )
    return PortfolioStateSnapshot(
        snapshot_id="state_1",
        portfolio_state=state,
        parent_snapshot_references=StateParentRefs(risk_snapshot_version="risk_old"),
        dataset_version="v1",
        pipeline_version="1.0",
        configuration_hash="abc"
    )

@pytest.fixture
def mock_exposure():
    analysis = PortfolioExposureAnalysis(
        sector_exposure=SectorExposure(sector_weights={"Technology": 50.0, "Financials": 50.0}),
        industry_exposure=IndustryExposure(industry_weights={"Consumer Electronics": 50.0, "Banking": 50.0}),
        gross_net_exposure=GrossNetExposure(gross_exposure=2100.0, net_exposure=2100.0, long_exposure=2100.0, short_exposure=0.0)
    )
    return PortfolioExposureSnapshot(
        snapshot_id="exp_1",
        exposure_analysis=analysis,
        parent_snapshot_references=StateParentRefs(risk_snapshot_version="risk_old"),
        dataset_version="v1",
        pipeline_version="1.0",
        configuration_hash="abc"
    )

@pytest.fixture
def mock_risk():
    mock = MagicMock(spec=RiskDecisionSnapshot)
    mock.snapshot_id = "risk_1"
    return mock

@pytest.fixture
def valid_context(mock_state, mock_exposure, mock_candidate, mock_risk):
    return PortfolioCorrelationExecutionContext(
        portfolio_state_snapshot=mock_state,
        portfolio_exposure_snapshot=mock_exposure,
        candidate_position_snapshot=mock_candidate,
        risk_decision_snapshot=mock_risk,
        configuration=PortfolioCorrelationConfigurationSnapshot(configuration_hash="conf_hash")
    )

@pytest.fixture
def pipeline_context(valid_context):
    return PortfolioCorrelationPipelineContext(
        execution_context=valid_context,
        execution_id="123"
    )

def test_structural_rules(valid_context):
    rules = PortfolioCorrelationStructuralRules()
    assert rules.validate(valid_context).is_valid
    
def test_consistency_rules(valid_context):
    rules = PortfolioCorrelationConsistencyRules()
    assert rules.validate(valid_context).is_valid
    
    invalid = valid_context.candidate_position_snapshot.model_copy(update={"dataset_version": "v2"})
    invalid_ctx = valid_context.model_copy(update={"candidate_position_snapshot": invalid})
    assert not rules.validate(invalid_ctx).is_valid

@pytest.mark.asyncio
async def test_symbol_correlation_stage(pipeline_context):
    stage = SymbolCorrelationStage()
    res = await stage.execute(pipeline_context)
    
    sym_corr = res.correlation_analysis.symbol_correlation
    assert next(p.correlation for p in sym_corr.pairwise_correlations if p.right_symbol == "AAPL") == 1.0
    assert next(p.correlation for p in sym_corr.pairwise_correlations if p.right_symbol == "JPM") == 0.5
    assert sym_corr.correlation_score == 0.75

@pytest.mark.asyncio
async def test_sector_correlation_stage(pipeline_context):
    stage = SectorCorrelationStage()
    res = await stage.execute(pipeline_context)
    
    sec_corr = res.correlation_analysis.sector_correlation
    assert sec_corr.candidate_sector_to_portfolio_correlation == 50.0
    assert next(s.correlation for s in sec_corr.sector_relationships if s.right_symbol == "Technology") == 1.0
    assert next(s.correlation for s in sec_corr.sector_relationships if s.right_symbol == "Financials") == 0.2

@pytest.mark.asyncio
async def test_industry_correlation_stage(pipeline_context):
    stage = IndustryCorrelationStage()
    res = await stage.execute(pipeline_context)
    
    ind_corr = res.correlation_analysis.industry_correlation
    assert ind_corr.candidate_industry_to_portfolio_correlation == 50.0
    assert next(i.correlation for i in ind_corr.industry_relationships if i.right_symbol == "Consumer Electronics") == 1.0
    assert next(i.correlation for i in ind_corr.industry_relationships if i.right_symbol == "Banking") == 0.1

@pytest.mark.asyncio
async def test_strategy_correlation_stage(pipeline_context):
    stage = StrategyCorrelationStage()
    res = await stage.execute(pipeline_context)
    
    strat_corr = res.correlation_analysis.strategy_correlation
    # AAPL matches symbol so overlap is 1 out of 2 positions = 0.5
    assert strat_corr.correlation_score == 0.5
    assert strat_corr.strategy_overlap == 50.0
    assert strat_corr.strategy_diversification == 50.0

@pytest.mark.asyncio
async def test_directional_correlation_stage(pipeline_context):
    stage = DirectionalCorrelationStage()
    res = await stage.execute(pipeline_context)
    
    dir_corr = res.correlation_analysis.directional_correlation
    # Portfolio is 100% long, candidate is long
    assert dir_corr.correlation_score == 1.0
    assert dir_corr.long_exposure_correlation == 1.0

@pytest.mark.asyncio
async def test_metrics_assembly_stage(pipeline_context):
    ctx = await SymbolCorrelationStage().execute(pipeline_context)
    ctx = await SectorCorrelationStage().execute(ctx)
    ctx = await IndustryCorrelationStage().execute(ctx)
    ctx = await StrategyCorrelationStage().execute(ctx)
    ctx = await DirectionalCorrelationStage().execute(ctx)
    
    res = await MetricsAssemblyStage().execute(ctx)
    metrics = res.correlation_metrics
    # Avg of (0.75, 0.6, 0.55, 0.5, 1.0) = 3.4 / 5 = 0.68
    assert round(metrics.average_correlation, 2) == 0.68
    assert metrics.maximum_correlation == 1.0

def test_snapshot_builder_missing_fields():
    builder = PortfolioCorrelationSnapshotBuilder()
    with pytest.raises(ValueError, match="required"):
        builder.build()

@pytest.mark.asyncio
async def test_single_position_portfolio(valid_context):
    positions = [
        OpenPosition(symbol="JPM", quantity=5, average_entry_price=100.0, current_price=110.0, sector="Financials", industry="Banking")
    ]
    single_state = valid_context.portfolio_state_snapshot.portfolio_state.model_copy(update={"positions": positions})
    single_snap = valid_context.portfolio_state_snapshot.model_copy(update={"portfolio_state": single_state})
    ctx = valid_context.model_copy(update={"portfolio_state_snapshot": single_snap})
    
    pipeline_ctx = PortfolioCorrelationPipelineContext(execution_context=ctx, execution_id="single")
    res = await SymbolCorrelationStage().execute(pipeline_ctx)
    
    # Candidate is AAPL, portfolio has only JPM (mock non-match is 0.5)
    assert res.correlation_analysis.symbol_correlation.correlation_score == 0.5


@pytest.mark.asyncio
async def test_empty_portfolio(valid_context):
    empty_state = valid_context.portfolio_state_snapshot.portfolio_state.model_copy(update={"positions": []})
    empty_snap = valid_context.portfolio_state_snapshot.model_copy(update={"portfolio_state": empty_state})
    ctx = valid_context.model_copy(update={"portfolio_state_snapshot": empty_snap})
    
    pipeline_ctx = PortfolioCorrelationPipelineContext(execution_context=ctx, execution_id="empty")
    res = await SymbolCorrelationStage().execute(pipeline_ctx)
    
    assert res.correlation_analysis.symbol_correlation.correlation_score == 0.0

@pytest.mark.asyncio
async def test_duplicate_symbols_in_portfolio(valid_context):
    # AAPL appears twice
    positions = [
        OpenPosition(symbol="AAPL", quantity=10, average_entry_price=150.0, current_price=155.0, sector="Technology", industry="Consumer Electronics"),
        OpenPosition(symbol="AAPL", quantity=5, average_entry_price=160.0, current_price=155.0, sector="Technology", industry="Consumer Electronics")
    ]
    dup_state = valid_context.portfolio_state_snapshot.portfolio_state.model_copy(update={"positions": positions})
    dup_snap = valid_context.portfolio_state_snapshot.model_copy(update={"portfolio_state": dup_state})
    ctx = valid_context.model_copy(update={"portfolio_state_snapshot": dup_snap})
    
    pipeline_ctx = PortfolioCorrelationPipelineContext(execution_context=ctx, execution_id="dup")
    res = await SymbolCorrelationStage().execute(pipeline_ctx)
    
    assert next(p.correlation for p in res.correlation_analysis.symbol_correlation.pairwise_correlations if p.right_symbol == "AAPL") == 1.0
    assert res.correlation_analysis.symbol_correlation.correlation_score == 1.0
