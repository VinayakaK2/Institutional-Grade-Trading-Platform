import pytest
from backend.paper_execution_quality_engine.validation.structural import StructuralValidator
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, ParentSnapshotReferences
from backend.paper_execution_quality_engine.builders.snapshot_builder import PaperExecutionQualitySnapshotBuilder
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.execution_quality import ExecutionQualityReport, MarketImpactMetrics, SlippageMetrics, SpreadMetrics, GapMetrics, LiquidityMetrics
from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityCalculationError
from backend.paper_execution_quality_engine.validation.consistency import ConsistencyValidator
import math

def test_structural_validator():
    val = StructuralValidator()
    ctx = PaperExecutionQualityExecutionContext(
        symbol="", timeframe="", dataset_version="",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version=""),
        configuration_hash="", execution_quality_model_version="", configuration={}
    )
    report = val.validate(ctx)
    assert not report.passed
    assert len(report.errors) == 6

def test_snapshot_builder_nan_validation():
    builder = PaperExecutionQualitySnapshotBuilder()
    
    report = ExecutionQualityReport(
        market_impact=MarketImpactMetrics(expected_execution_price=50000, market_impact=math.nan, impact_percentage=0.0, impact_cost=0.0),
        slippage=SlippageMetrics(expected_price=50000, actual_fill_price=50000, slippage_amount=0.0, slippage_percentage=0.0),
        spread_cost=SpreadMetrics(bid_price=49900, ask_price=50100, mid_price=50000, effective_spread=200, paid_spread=100),
        gap_cost=GapMetrics(gap_up=False, gap_down=False, gap_size=0.0, gap_impact=0.0),
        liquidity_metrics=LiquidityMetrics(available_liquidity=100, executed_quantity=25, remaining_liquidity=75, liquidity_utilization=25)
    )
    
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill1"),
        configuration_hash="hash1", execution_quality_model_version="v1"
    )
    pipeline = PaperExecutionQualityPipelineContext(execution_context=ctx)
    pipeline.execution_quality_report = report
    
    with pytest.raises(PaperExecutionQualityCalculationError, match="Market impact must be finite."):
        builder.build(ctx, pipeline)

@pytest.mark.asyncio
async def test_consistency_validator_no_repo():
    val = ConsistencyValidator()
    ctx = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="fill1"),
        configuration_hash="hash1", execution_quality_model_version="v1"
    )
    report = await val.validate(ctx)
    # Passed should be True because it skips gracefully if no repo is provided, or we should raise an error?
    # Based on the code: if self._paper_fill_repository: ... else: it just returns empty report.
    assert report.passed

class MockFillRepo:
    def load(self, version):
        if version == "missing":
            return None
        if version == "error":
            raise ValueError("DB Error")
        return {"id": version}

@pytest.mark.asyncio
async def test_consistency_validator_with_repo():
    repo = MockFillRepo()
    val = ConsistencyValidator(paper_fill_repository=repo)
    
    # Missing
    ctx1 = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="missing"),
        configuration_hash="hash1", execution_quality_model_version="v1"
    )
    r1 = await val.validate(ctx1)
    assert not r1.passed
    assert "does not exist" in r1.errors[0]

    # Error
    ctx2 = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="error"),
        configuration_hash="hash1", execution_quality_model_version="v1"
    )
    r2 = await val.validate(ctx2)
    assert not r2.passed
    assert "DB Error" in r2.errors[0]
    
    # Found
    ctx3 = PaperExecutionQualityExecutionContext(
        symbol="BTC/USD", timeframe="1h", dataset_version="v1",
        parent_snapshot_references=ParentSnapshotReferences(parent_fill_snapshot_version="found"),
        configuration_hash="hash1", execution_quality_model_version="v1"
    )
    r3 = await val.validate(ctx3)
    assert r3.passed
