import pytest
from backend.risk_engine.config.config import RiskEngineConfig
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.validation.structural import StructuralValidationLayer
from backend.risk_engine.validation.consistency import ConsistencyValidationLayer
from backend.risk_engine.pipeline.pipeline import RiskPipeline
from backend.risk_engine.pipeline.contracts import IRiskPipelineStage
from backend.risk_engine.core.engine import RiskEngine
from backend.risk_engine.core.builder import RiskSnapshotBuilder
from backend.risk_engine.contracts.repository import IRiskSnapshotRepository
from backend.risk_engine.contracts.query_service import IRiskSnapshotQueryService
from backend.risk_engine.models.snapshot import RiskSnapshot, PipelineResult, ValidationResult, RiskMetadata
from backend.risk_engine.exceptions.exceptions import RiskValidationError

@pytest.fixture
def base_config():
    return RiskEngineConfig()

@pytest.fixture
def valid_context(base_config):
    return RiskExecutionContext(
        symbol="AAPL",
        timeframe="1D",
        dataset_version=1,
        parent_trade_decision_snapshot_version="tds_123",
        configuration=base_config,
        metadata={"test": True}
    )

class MockRepository(IRiskSnapshotRepository):
    def __init__(self):
        self.snapshots = {}
        
    async def save(self, snapshot: RiskSnapshot) -> None:
        self.snapshots[snapshot.snapshot_id] = snapshot
        
    async def load(self, snapshot_id: str):
        return self.snapshots.get(snapshot_id)
        
    async def exists(self, snapshot_id: str) -> bool:
        return snapshot_id in self.snapshots
        
    async def query_by_symbol(self, symbol: str):
        return [s for s in self.snapshots.values() if s.context.symbol == symbol]
        
    async def query_by_timeframe(self, timeframe: str):
        return [s for s in self.snapshots.values() if s.context.timeframe == timeframe]
        
    async def query_by_parent_trade_decision_snapshot(self, parent_id: str):
        return [s for s in self.snapshots.values() if s.context.parent_trade_decision_snapshot_version == parent_id]
        
    async def load_latest(self, symbol: str, timeframe: str):
        matches = [s for s in self.snapshots.values() if s.context.symbol == symbol and s.context.timeframe == timeframe]
        return matches[-1] if matches else None

class MockQueryService(IRiskSnapshotQueryService):
    async def load(self, snapshot_id: str): pass
    async def query_by_symbol(self, symbol: str): pass
    async def query_by_parent_trade_decision_snapshot(self, parent_id: str): pass
    async def load_latest(self, symbol: str, timeframe: str): pass

class MockStage(IRiskPipelineStage):
    def __init__(self, name, should_fail=False):
        self._name = name
        self._should_fail = should_fail
        
    @property
    def stage_name(self) -> str:
        return self._name
        
    async def execute(self, context):
        if self._should_fail:
            raise ValueError(f"{self._name} failed")
        return {"done": True}

@pytest.mark.asyncio
async def test_structural_validation(valid_context):
    layer = StructuralValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    bad_ctx1 = valid_context.model_copy(update={"symbol": ""})
    res_bad1 = await layer.validate(bad_ctx1)
    assert not res_bad1.is_valid
    assert "Symbol cannot be empty" in res_bad1.errors[0]
    
    bad_ctx2 = valid_context.model_copy(update={"timeframe": ""})
    res_bad2 = await layer.validate(bad_ctx2)
    assert not res_bad2.is_valid
    assert "Timeframe cannot be empty" in res_bad2.errors[0]
    
    bad_ctx3 = valid_context.model_copy(update={"dataset_version": 0})
    res_bad3 = await layer.validate(bad_ctx3)
    assert not res_bad3.is_valid
    assert "Dataset version must be strictly positive" in res_bad3.errors[0]
    
    bad_ctx4 = valid_context.model_copy(update={"parent_trade_decision_snapshot_version": ""})
    res_bad4 = await layer.validate(bad_ctx4)
    assert not res_bad4.is_valid
    assert "Parent snapshot version must be provided" in res_bad4.errors[0]
    
    bad_ctx5 = valid_context.model_copy()
    object.__setattr__(bad_ctx5, 'configuration', None) # bypass pydantic validation for testing structural logic
    res_bad5 = await layer.validate(bad_ctx5)
    assert not res_bad5.is_valid
    assert "Configuration is strictly required" in res_bad5.errors[0]

@pytest.mark.asyncio
async def test_consistency_validation(valid_context):
    layer = ConsistencyValidationLayer()
    res = await layer.validate(valid_context)
    assert res.is_valid
    
    bad_ctx = valid_context.model_copy(update={"parent_trade_decision_snapshot_version": "MOCK_INVALID_PARENT"})
    res_bad = await layer.validate(bad_ctx)
    assert not res_bad.is_valid
    assert "lineage validation failed" in res_bad.errors[0]
    
    bad_ctx2 = valid_context.model_copy(update={"dataset_version": 1000000})
    res_bad2 = await layer.validate(bad_ctx2)
    assert not res_bad2.is_valid
    assert "out of logical bounds" in res_bad2.errors[0]

@pytest.mark.asyncio
async def test_pipeline_execution(valid_context):
    pipeline = RiskPipeline()
    res = await pipeline.execute(valid_context)
    assert res.success
    
    pipeline.register_stage(MockStage("Stage1"))
    res = await pipeline.execute(valid_context)
    assert res.success
    assert "Stage1" in res.stage_results
    assert res.stage_results["Stage1"]["status"] == "PASS"

@pytest.mark.asyncio
async def test_pipeline_fail_fast(valid_context):
    pipeline = RiskPipeline([MockStage("Stage1", should_fail=True), MockStage("Stage2")])
    res = await pipeline.execute(valid_context)
    
    assert not res.success
    assert "Stage1" in res.stage_results
    assert res.stage_results["Stage1"]["status"] == "FAIL"
    assert "Stage2" not in res.stage_results

@pytest.mark.asyncio
async def test_pipeline_no_fail_fast(valid_context):
    # Set fail_fast to False
    cfg = RiskEngineConfig(fail_fast=False)
    ctx = valid_context.model_copy(update={"configuration": cfg})
    pipeline = RiskPipeline([MockStage("Stage1", should_fail=True), MockStage("Stage2")])
    res = await pipeline.execute(ctx)
    
    assert res.success
    assert "Stage1" in res.stage_results
    assert res.stage_results["Stage1"]["status"] == "FAIL"
    assert "Stage2" in res.stage_results

def test_builder_determinism(valid_context):
    pr = PipelineResult(success=True, stage_results={})
    vr = ValidationResult(is_valid=True, errors=[])
    md = RiskMetadata(pipeline_version="1.0.0", execution_duration_ms=10)
    
    s1 = RiskSnapshotBuilder.build(valid_context, pr, vr, md)
    s2 = RiskSnapshotBuilder.build(valid_context, pr, vr, md)
    
    assert s1.snapshot_id == s2.snapshot_id

@pytest.mark.asyncio
async def test_engine_execution(valid_context):
    repo = MockRepository()
    pipeline = RiskPipeline()
    engine = RiskEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=pipeline,
        repository=repo
    )
    
    snapshot = await engine.execute(valid_context)
    assert snapshot.snapshot_id is not None
    assert snapshot.validation_status.is_valid
    assert snapshot.pipeline_result.success
    
    loaded = await repo.load(snapshot.snapshot_id)
    assert loaded == snapshot

@pytest.mark.asyncio
async def test_engine_validation_failure(valid_context):
    repo = MockRepository()
    pipeline = RiskPipeline()
    engine = RiskEngine(
        validation_layers=[StructuralValidationLayer(), ConsistencyValidationLayer()],
        pipeline=pipeline,
        repository=repo
    )
    
    bad_ctx = valid_context.model_copy(update={"symbol": ""})
    with pytest.raises(RiskValidationError):
        await engine.execute(bad_ctx)

def test_immutability(valid_context):
    with pytest.raises(Exception):
        valid_context.symbol = "NEW"

@pytest.mark.asyncio
async def test_mock_query_service():
    svc = MockQueryService()
    await svc.load("123")
    await svc.query_by_symbol("AAPL")
    await svc.query_by_parent_trade_decision_snapshot("123")
    await svc.load_latest("AAPL", "1D")
