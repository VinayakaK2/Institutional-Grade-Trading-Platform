import pytest
from backend.position_risk_engine.config.config import PositionRiskConfig
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.validation.structural import StructuralValidationLayer
from backend.position_risk_engine.validation.consistency import ConsistencyValidationLayer
from backend.position_risk_engine.pipeline.pipeline import PositionRiskPipeline
from backend.position_risk_engine.pipeline.metrics.entry_price import EntryPriceMetric
from backend.position_risk_engine.pipeline.metrics.stop_loss import StopLossMetric
from backend.position_risk_engine.pipeline.metrics.distance import StopLossDistanceMetric
from backend.position_risk_engine.pipeline.metrics.absolute_risk import AbsoluteRiskMetric
from backend.position_risk_engine.pipeline.metrics.percentage_risk import PercentageRiskMetric
from backend.position_risk_engine.pipeline.metrics.per_unit_risk import PerUnitRiskMetric
from backend.position_risk_engine.core.engine import PositionRiskEvaluationEngine
from backend.position_risk_engine.core.builder import RiskEvaluationSnapshotBuilder
from backend.position_risk_engine.contracts.repository import IPositionRiskSnapshotRepository
from backend.position_risk_engine.contracts.query_service import IPositionRiskQueryService
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot, PositionRiskMetadata
from backend.position_risk_engine.models.report import RiskEvaluationReport, ValidationResult
from backend.position_risk_engine.exceptions.exceptions import PositionRiskValidationError
from backend.position_risk_engine.pipeline.contracts import IRiskMetricStage

@pytest.fixture
def base_config():
    return PositionRiskConfig()

@pytest.fixture
def valid_context(base_config):
    return PositionRiskEvaluationContext(
        symbol="AAPL",
        timeframe="1D",
        trade_decision_snapshot_version="tds_123",
        entry_price=150.0,
        initial_stop_loss=140.0,
        instrument_metadata={"multiplier": 2.0},
        configuration=base_config,
        metadata={"test": True}
    )

class MockRepository(IPositionRiskSnapshotRepository):
    def __init__(self):
        self.snapshots = {}
        
    async def save(self, snapshot: RiskEvaluationSnapshot) -> None:
        self.snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str):
        return self.snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self.snapshots
        
    async def query_by_symbol(self, symbol: str):
        return [s for s in self.snapshots.values() if s.context.symbol == symbol]
        
    async def query_by_timeframe(self, timeframe: str):
        return [s for s in self.snapshots.values() if s.context.timeframe == timeframe]
        
    async def query_by_trade_decision_snapshot(self, parent_id: str):
        return [s for s in self.snapshots.values() if s.context.trade_decision_snapshot_version == parent_id]
        
    async def load_latest(self, symbol: str, timeframe: str):
        matches = [s for s in self.snapshots.values() if s.context.symbol == symbol and s.context.timeframe == timeframe]
        if not matches:
            return None
        return sorted(matches, key=lambda x: x.created_at, reverse=True)[0]

class MockQueryService(IPositionRiskQueryService):
    async def load(self, snapshot_id: str): pass
    async def load_latest(self, symbol: str, timeframe: str): pass
    async def query_by_symbol(self, symbol: str): pass
    async def query_by_dataset_version(self, version: int): pass

@pytest.mark.asyncio
async def test_structural_validation(valid_context):
    layer = StructuralValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    # Empty symbol
    bad_ctx1 = valid_context.model_copy(update={"symbol": ""})
    res_bad1 = await layer.validate(bad_ctx1)
    assert not res_bad1.is_valid
    assert "Symbol is required" in res_bad1.errors[0]
    
    # Empty timeframe
    bad_ctx2 = valid_context.model_copy(update={"timeframe": ""})
    res_bad2 = await layer.validate(bad_ctx2)
    assert not res_bad2.is_valid
    assert "Timeframe is required" in res_bad2.errors[0]
    
    # Negative entry
    bad_ctx3 = valid_context.model_copy(update={"entry_price": -10})
    res_bad3 = await layer.validate(bad_ctx3)
    assert not res_bad3.is_valid
    assert "Entry price must be strictly positive" in res_bad3.errors[0]
    
    # Negative stop loss
    bad_ctx4 = valid_context.model_copy(update={"initial_stop_loss": 0})
    res_bad4 = await layer.validate(bad_ctx4)
    assert not res_bad4.is_valid
    assert "Initial stop loss must be strictly positive" in res_bad4.errors[0]
    
    # Identical prices
    bad_ctx5 = valid_context.model_copy(update={"initial_stop_loss": 150.0})
    res_bad5 = await layer.validate(bad_ctx5)
    assert not res_bad5.is_valid
    assert "cannot be identical" in res_bad5.errors[0]
    
    # No configuration
    bad_ctx6 = valid_context.model_copy()
    object.__setattr__(bad_ctx6, 'configuration', None)
    res_bad6 = await layer.validate(bad_ctx6)
    assert not res_bad6.is_valid
    assert "Configuration is strictly required" in res_bad6.errors[0]

@pytest.mark.asyncio
async def test_consistency_validation(valid_context):
    layer = ConsistencyValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    # Invalid lineage
    bad_ctx1 = valid_context.model_copy(update={"trade_decision_snapshot_version": "MOCK_INVALID"})
    res_bad1 = await layer.validate(bad_ctx1)
    assert not res_bad1.is_valid
    assert "lineage validation failed" in res_bad1.errors[0]

@pytest.mark.asyncio
async def test_metrics(valid_context):
    # Entry
    m_entry = EntryPriceMetric()
    assert m_entry.stage_name == "entry_price"
    e_entry = await m_entry.calculate(valid_context)
    assert e_entry.entry_price == 150.0
    
    # Stop Loss
    m_sl = StopLossMetric()
    assert m_sl.stage_name == "stop_loss"
    e_sl = await m_sl.calculate(valid_context)
    assert e_sl.stop_loss == 140.0
    
    # Distance
    m_dist = StopLossDistanceMetric()
    assert m_dist.stage_name == "distance"
    e_dist = await m_dist.calculate(valid_context)
    assert e_dist.risk_distance == 10.0
    
    # Absolute Risk
    m_abs = AbsoluteRiskMetric()
    assert m_abs.stage_name == "absolute_risk"
    e_abs = await m_abs.calculate(valid_context)
    assert e_abs.absolute_risk == 10.0
    
    # Percentage Risk
    m_pct = PercentageRiskMetric()
    assert m_pct.stage_name == "percentage_risk"
    e_pct = await m_pct.calculate(valid_context)
    assert e_pct.percentage_risk == pytest.approx(10.0 / 150.0)
    
    # Per Unit Risk
    m_pu = PerUnitRiskMetric()
    assert m_pu.stage_name == "per_unit_risk"
    e_pu = await m_pu.calculate(valid_context)
    assert e_pu.risk_per_unit == 20.0 # distance * multiplier = 10 * 2 = 20
    
    # Edge case Percentage Risk Entry=0
    bad_ctx_zero = valid_context.model_copy(update={"entry_price": 0})
    e_pct_zero = await m_pct.calculate(bad_ctx_zero)
    assert e_pct_zero.percentage_risk == 0.0

@pytest.mark.asyncio
async def test_pipeline(valid_context):
    pipeline = PositionRiskPipeline([
        EntryPriceMetric(),
        StopLossMetric(),
        AbsoluteRiskMetric()
    ])
    
    results = await pipeline.execute(valid_context)
    assert "entry_price" in results
    assert "stop_loss" in results
    assert "absolute_risk" in results

class BadMetric(IRiskMetricStage):
    @property
    def stage_name(self) -> str: return "bad"
    async def calculate(self, ctx): raise ValueError("Fail")

@pytest.mark.asyncio
async def test_pipeline_fail_fast(valid_context):
    pipeline = PositionRiskPipeline([BadMetric()])
    with pytest.raises(ValueError, match="Fail"):
        await pipeline.execute(valid_context)
        
    cfg = PositionRiskConfig(fail_fast=False)
    ctx_no_fail = valid_context.model_copy(update={"configuration": cfg})
    results = await pipeline.execute(ctx_no_fail)
    assert "bad" not in results

def test_builder_determinism(valid_context):
    vr = ValidationResult(is_valid=True, errors=[])
    report = RiskEvaluationReport(
        validation_status=vr,
        configuration_version="1.0.0",
        algorithm_version="1.0.0"
    )
    metadata = PositionRiskMetadata(execution_duration_ms=10)
    
    s1 = RiskEvaluationSnapshotBuilder.build(valid_context, report, metadata)
    s2 = RiskEvaluationSnapshotBuilder.build(valid_context, report, metadata)
    assert s1.snapshot_id == s2.snapshot_id

@pytest.mark.asyncio
async def test_engine_execution(valid_context):
    repo = MockRepository()
    pipeline = PositionRiskPipeline([
        EntryPriceMetric(),
        StopLossDistanceMetric()
    ])
    engine = PositionRiskEvaluationEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=pipeline,
        repository=repo
    )
    
    snapshot = await engine.execute(valid_context)
    assert snapshot.snapshot_id is not None
    assert snapshot.report.validation_status.is_valid
    assert snapshot.report.entry_evidence.entry_price == 150.0
    assert snapshot.report.distance_evidence.risk_distance == 10.0
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_engine_validation_failure(valid_context):
    repo = MockRepository()
    pipeline = PositionRiskPipeline()
    engine = PositionRiskEvaluationEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=pipeline,
        repository=repo
    )
    
    bad_ctx = valid_context.model_copy(update={"symbol": ""})
    with pytest.raises(PositionRiskValidationError):
        await engine.execute(bad_ctx)

def test_immutability(valid_context):
    with pytest.raises(Exception):
        valid_context.symbol = "NEW"

@pytest.mark.asyncio
async def test_mock_query_service():
    svc = MockQueryService()
    await svc.load("123")
    await svc.query_by_symbol("AAPL")
    await svc.query_by_dataset_version(1)
    await svc.load_latest("AAPL", "1D")
