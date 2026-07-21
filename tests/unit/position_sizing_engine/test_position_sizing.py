import pytest
from backend.position_sizing_engine.config.config import PositionSizingConfig
from backend.position_sizing_engine.models.context import PositionSizingContext, ParentRiskSnapshotReference
from backend.position_sizing_engine.validation.structural import StructuralValidationLayer
from backend.position_sizing_engine.validation.consistency import ConsistencyValidationLayer
from backend.position_sizing_engine.pipeline.pipeline import PositionSizingPipeline
from backend.position_sizing_engine.pipeline.stages.capital_allocation import CapitalAllocationStage
from backend.position_sizing_engine.pipeline.stages.maximum_risk import MaximumRiskStage
from backend.position_sizing_engine.pipeline.stages.raw_position_size import RawPositionSizeStage
from backend.position_sizing_engine.pipeline.stages.round_lot_adjustment import RoundLotAdjustmentStage
from backend.position_sizing_engine.pipeline.stages.remaining_cash import RemainingCashStage
from backend.position_sizing_engine.pipeline.policies.round_lot import EquityRoundLotPolicy, FractionalAssetPolicy
from backend.position_sizing_engine.pipeline.policies.registry import RoundLotPolicyRegistry
from backend.position_sizing_engine.core.engine import PositionSizingEngine
from backend.position_sizing_engine.core.builder import PositionSizingSnapshotBuilder
from backend.position_sizing_engine.contracts.repository import IPositionSizingSnapshotRepository
from backend.position_sizing_engine.contracts.query_service import IPositionSizingQueryService
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot, PositionSizingMetadata
from backend.position_sizing_engine.models.report import PositionSizingReport, ValidationResult
from backend.position_sizing_engine.exceptions.exceptions import PositionSizingValidationError

# Mock imports for RiskEvaluationSnapshot setup
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.report import RiskEvaluationReport, ValidationResult as RiskValidationResult
from backend.position_risk_engine.models.evidence import PerUnitRiskEvidence, EntryEvidence
from backend.position_risk_engine.config.config import PositionRiskConfig

@pytest.fixture
def risk_snapshot():
    pr_config = PositionRiskConfig()
    ctx = PositionRiskEvaluationContext(
        symbol="AAPL", timeframe="1D", trade_decision_snapshot_version="tds_1",
        entry_price=100.0, initial_stop_loss=90.0, configuration=pr_config
    )
    rep = RiskEvaluationReport(
        validation_status=RiskValidationResult(is_valid=True),
        entry_evidence=EntryEvidence(calculation_method="test", entry_price=100.0, source_snapshot_id="tds_1"),
        per_unit_risk_evidence=PerUnitRiskEvidence(calculation_method="test", source_snapshot_id="tds_1", entry_price=100.0, stop_loss=90.0, risk_per_unit=10.0),
        configuration_version="1.0.0", algorithm_version="1.0.0"
    )
    from backend.position_risk_engine.core.builder import RiskEvaluationSnapshotBuilder
    from backend.position_risk_engine.models.snapshot import PositionRiskMetadata
    return RiskEvaluationSnapshotBuilder.build(ctx, rep, PositionRiskMetadata(execution_duration_ms=1))

@pytest.fixture
def base_config():
    return PositionSizingConfig()

@pytest.fixture
def valid_context(base_config, risk_snapshot):
    ref = ParentRiskSnapshotReference(
        snapshot_id=risk_snapshot.snapshot_id,
        snapshot_version="1.0.0",
        dataset_version="v1",
        configuration_hash="hash1"
    )
    return PositionSizingContext(
        parent_risk_snapshot=ref,
        risk_evaluation_snapshot=risk_snapshot,
        available_capital=10000.0,
        allocation_configuration={"allocation_pct": 1.0, "max_risk_pct": 0.02},
        configuration=base_config
    )

class MockRepository(IPositionSizingSnapshotRepository):
    def __init__(self):
        self.snapshots = {}
        
    async def save(self, snapshot: PositionSizingSnapshot) -> None:
        self.snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str):
        return self.snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self.snapshots
        
    async def query_by_symbol(self, symbol: str):
        return [s for s in self.snapshots.values() if s.context.risk_evaluation_snapshot.context.symbol == symbol]
        
    async def query_by_timeframe(self, timeframe: str):
        return [s for s in self.snapshots.values() if s.context.risk_evaluation_snapshot.context.timeframe == timeframe]
        
    async def query_by_parent_risk_snapshot(self, parent_id: str):
        return [s for s in self.snapshots.values() if s.context.parent_risk_snapshot.snapshot_id == parent_id]
        
    async def query_by_dataset_version(self, dataset_version: str):
        return [s for s in self.snapshots.values() if s.context.parent_risk_snapshot.dataset_version == dataset_version]
        
    async def load_latest(self, symbol: str, timeframe: str):
        return None

class MockQueryService(IPositionSizingQueryService):
    async def load(self, snapshot_id: str): pass
    async def load_latest(self, symbol: str, timeframe: str): pass
    async def query_by_symbol(self, symbol: str): pass
    async def query_by_dataset_version(self, version: str): pass

@pytest.mark.asyncio
async def test_structural_validation(valid_context):
    layer = StructuralValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    # Negative capital
    bad_ctx1 = valid_context.model_copy(update={"available_capital": -100})
    res_bad1 = await layer.validate(bad_ctx1)
    assert not res_bad1.is_valid
    assert "Available capital must be strictly positive" in res_bad1.errors[0]
    
    # Missing alloc pct
    bad_ctx2 = valid_context.model_copy(update={"allocation_configuration": {"max_risk_pct": 0.02}})
    res_bad2 = await layer.validate(bad_ctx2)
    assert not res_bad2.is_valid
    assert "must contain 'allocation_pct'" in res_bad2.errors[0]

@pytest.mark.asyncio
async def test_consistency_validation(valid_context):
    layer = ConsistencyValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    # Mismatch snapshot ids
    ref_bad = ParentRiskSnapshotReference(
        snapshot_id="different_id",
        snapshot_version="1.0.0", dataset_version="v1", configuration_hash="h"
    )
    bad_ctx = valid_context.model_copy(update={"parent_risk_snapshot": ref_bad})
    res_bad = await layer.validate(bad_ctx)
    assert not res_bad.is_valid
    assert "Risk Evaluation Snapshot ID does not match" in res_bad.errors[0]

@pytest.mark.asyncio
async def test_stages(valid_context):
    # Stage 1: Allocation
    s1 = CapitalAllocationStage()
    e1 = await s1.calculate(valid_context, {})
    assert e1.allocated_capital == 10000.0
    
    # Stage 2: Max Risk
    s2 = MaximumRiskStage()
    with pytest.raises(ValueError):
        await s2.calculate(valid_context, {}) # Missing prerequisite
    e2 = await s2.calculate(valid_context, {"capital_allocation": e1})
    assert e2.max_risk_amount == 200.0 # 2% of 10k
    
    # Stage 3: Raw Size
    s3 = RawPositionSizeStage()
    e3 = await s3.calculate(valid_context, {"maximum_risk": e2})
    assert e3.raw_position_size == 20.0 # 200 risk / 10 per unit
    
    registry = RoundLotPolicyRegistry()
    registry.register("equity", EquityRoundLotPolicy())
    registry.register("crypto", FractionalAssetPolicy(2))
    
    # Stage 4: Round Lot
    s4 = RoundLotAdjustmentStage(registry)
    e4 = await s4.calculate(valid_context, {"raw_position_size": e3})
    assert e4.rounded_position_size == 20.0
    
    # Fractional policy test
    # If raw was 20.55555
    e3_frac = e3.model_copy(update={"raw_position_size": 20.55555})
    valid_context_frac = valid_context.model_copy(update={"instrument_metadata": {"asset_type": "crypto"}})
    e4_frac = await s4.calculate(valid_context_frac, {"raw_position_size": e3_frac})
    assert e4_frac.rounded_position_size == 20.56
    
    # Stage 5: Remaining Cash
    s5 = RemainingCashStage()
    e5 = await s5.calculate(valid_context, {"capital_allocation": e1, "round_lot_adjustment": e4})
    # cost = 20 * 100 = 2000
    # remaining = 10000 - 2000 = 8000
    assert e5.position_cost == 2000.0
    assert e5.remaining_cash == 8000.0

@pytest.mark.asyncio
async def test_engine_execution_and_determinism(valid_context):
    repo = MockRepository()
    registry = RoundLotPolicyRegistry()
    registry.register("equity", EquityRoundLotPolicy())
    
    pipeline = PositionSizingPipeline([
        CapitalAllocationStage(),
        MaximumRiskStage(),
        RawPositionSizeStage(),
        RoundLotAdjustmentStage(registry),
        RemainingCashStage()
    ])
    
    engine = PositionSizingEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=pipeline,
        repository=repo
    )
    
    snapshot1 = await engine.execute(valid_context)
    assert snapshot1.snapshot_id is not None
    assert snapshot1.report.remaining_cash_evidence.remaining_cash == 8000.0
    
    # Determinism Regression Test
    # Running exactly the same inputs should produce EXACTLY the same snapshot ID, 
    # despite execution duration and timestamps being different.
    
    # Sleep to ensure different metadata generation time
    import time
    time.sleep(0.01)
    
    snapshot2 = await engine.execute(valid_context)
    assert snapshot1.snapshot_id == snapshot2.snapshot_id

@pytest.mark.asyncio
async def test_mock_query_service():
    svc = MockQueryService()
    await svc.load("123")
    await svc.query_by_symbol("AAPL")
    await svc.query_by_dataset_version("v1")
    await svc.load_latest("AAPL", "1D")
