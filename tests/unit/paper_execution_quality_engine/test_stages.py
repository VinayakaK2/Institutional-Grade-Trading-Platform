import pytest
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext, ParentSnapshotReferences
from backend.paper_execution_quality_engine.core.stages.market_impact import MarketImpactStage
from backend.paper_execution_quality_engine.core.stages.slippage import SlippageStage
from backend.paper_execution_quality_engine.core.stages.spread import SpreadStage
from backend.paper_execution_quality_engine.core.stages.gap import GapStage
from backend.paper_execution_quality_engine.core.stages.liquidity import LiquidityStage

@pytest.fixture
def empty_pipeline_context():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD",
        timeframe="1h",
        dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123",
        execution_quality_model_version="v1",
        configuration={}
    )
    return PaperExecutionQualityPipelineContext(execution_context=ctx)

@pytest.mark.asyncio
async def test_market_impact_stage_zero():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"market_impact": {"expected_execution_price": 50000, "impact_percentage": 0.0}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = MarketImpactStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.market_impact_result.market_impact == 0.0
    assert pipeline.market_impact_result.impact_cost == 0.0

@pytest.mark.asyncio
async def test_market_impact_stage_positive():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"market_impact": {"expected_execution_price": 50000, "impact_percentage": 1.0}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = MarketImpactStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.market_impact_result.market_impact == 500.0

@pytest.mark.asyncio
async def test_slippage_stage_zero():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"slippage": {"expected_price": 50000, "actual_fill_price": 50000}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = SlippageStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.slippage_result.slippage_amount == 0.0
    assert pipeline.slippage_result.slippage_percentage == 0.0

@pytest.mark.asyncio
async def test_slippage_stage_positive():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"slippage": {"expected_price": 50000, "actual_fill_price": 50100}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = SlippageStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.slippage_result.slippage_amount == 100.0
    assert pipeline.slippage_result.slippage_percentage == 0.2

@pytest.mark.asyncio
async def test_slippage_stage_negative():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"slippage": {"expected_price": 50000, "actual_fill_price": 49900}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = SlippageStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.slippage_result.slippage_amount == -100.0
    assert pipeline.slippage_result.slippage_percentage == -0.2

@pytest.mark.asyncio
async def test_spread_stage_calculations():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"spread": {"bid_price": 49900, "ask_price": 50100}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = SpreadStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.spread_result.mid_price == 50000.0
    assert pipeline.spread_result.effective_spread == 200.0
    assert pipeline.spread_result.paid_spread == 100.0

@pytest.mark.asyncio
async def test_gap_stage():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"gap": {"gap_up": True, "gap_size": 500, "gap_impact": 200}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = GapStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.gap_result.gap_up is True
    assert pipeline.gap_result.gap_down is False
    assert pipeline.gap_result.gap_size == 500.0
    assert pipeline.gap_result.gap_impact == 200.0

@pytest.mark.asyncio
async def test_liquidity_stage_sufficient():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"liquidity": {"available_liquidity": 100.0, "executed_quantity": 25.0}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = LiquidityStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.liquidity_result.remaining_liquidity == 75.0
    assert pipeline.liquidity_result.liquidity_utilization == 25.0

@pytest.mark.asyncio
async def test_liquidity_stage_zero():
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill_v1"),
        configuration_hash="hash_123", execution_quality_model_version="v1",
        configuration={"liquidity": {"available_liquidity": 0.0, "executed_quantity": 0.0}}
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    stage = LiquidityStage()
    await stage.execute(ctx, pipeline)
    
    assert pipeline.liquidity_result.remaining_liquidity == 0.0
    assert pipeline.liquidity_result.liquidity_utilization == 0.0
