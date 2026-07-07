import pytest
from datetime import datetime, timezone
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.universe_engine.models.universe import UniverseInstrument, InstrumentType, TradingStatus, MarketSegment
from backend.universe_engine.contracts.pipeline import IUniverseStage
from backend.universe_engine.models.universe import UniverseExecutionContext, StageResult, StageStatus
from backend.universe_engine.models.exceptions import UniversePipelineError
from backend.universe_engine.models.config import PipelineSettings
from backend.universe_engine.pipeline.pipeline import UniverseExecutionPipeline

class MockStage(IUniverseStage):
    def __init__(self, name: str, status: StageStatus = StageStatus.SUCCESS):
        self._name = name
        self._status = status
        
    @property
    def name(self) -> str:
        return self._name
        
    async def execute(self, context: UniverseExecutionContext) -> StageResult:
        return StageResult(
            stage_name=self.name,
            status=self._status,
            duration_ms=10.0,
            metadata={"mock": True}
        )

class MockExceptionStage(IUniverseStage):
    @property
    def name(self) -> str:
        return "ExceptionStage"
        
    async def execute(self, context: UniverseExecutionContext) -> StageResult:
        raise ValueError("Mock exception")

@pytest.fixture
def base_context():
    return UniverseExecutionContext(
        run_id="test-run",
        snapshot_id="test-snapshot",
        provider_name="test-provider",
        started_at=datetime.now(timezone.utc),
        instruments=[UniverseInstrument(symbol=SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ")), instrument_type=InstrumentType.EQUITY, trading_status=TradingStatus.ACTIVE, market_segment=MarketSegment.EQUITY_CASH, is_delisted=False)],
        shared_state={},
        metadata={},
        stage_results=[]
    )

@pytest.mark.asyncio
async def test_pipeline_registration_limit():
    settings = PipelineSettings(max_stages=1)
    pipeline = UniverseExecutionPipeline(settings)
    
    pipeline.register_stage(MockStage("Stage 1"))
    
    with pytest.raises(UniversePipelineError) as exc:
        pipeline.register_stage(MockStage("Stage 2"))
        
    assert "Maximum pipeline stages" in str(exc.value)

@pytest.mark.asyncio
async def test_pipeline_execution_success(base_context):
    settings = PipelineSettings()
    pipeline = UniverseExecutionPipeline(settings)
    
    pipeline.register_stage(MockStage("Stage 1"))
    pipeline.register_stage(MockStage("Stage 2"))
    
    result_context = await pipeline.execute(base_context)
    
    assert len(result_context.stage_results) == 2
    assert result_context.stage_results[0].stage_name == "Stage 1"
    assert result_context.stage_results[1].stage_name == "Stage 2"

@pytest.mark.asyncio
async def test_pipeline_execution_halt_on_failure(base_context):
    settings = PipelineSettings()
    pipeline = UniverseExecutionPipeline(settings)
    
    pipeline.register_stage(MockStage("Stage 1", status=StageStatus.SUCCESS))
    pipeline.register_stage(MockStage("Stage 2", status=StageStatus.FAILED))
    pipeline.register_stage(MockStage("Stage 3", status=StageStatus.SUCCESS))
    
    result_context = await pipeline.execute(base_context)
    
    # Should halt after Stage 2
    assert len(result_context.stage_results) == 2
    assert result_context.stage_results[-1].status == StageStatus.FAILED

@pytest.mark.asyncio
async def test_pipeline_execution_exception_handling(base_context):
    settings = PipelineSettings()
    pipeline = UniverseExecutionPipeline(settings)
    
    pipeline.register_stage(MockExceptionStage())
    
    with pytest.raises(UniversePipelineError) as exc:
        await pipeline.execute(base_context)
        
    assert "Mock exception" in str(exc.value.details)
    assert len(base_context.stage_results) == 1
    assert base_context.stage_results[0].status == StageStatus.FAILED
    assert "Unhandled exception" in base_context.stage_results[0].warnings[0]

