import pytest
from typing import Dict, Any

from backend.trade_validation_engine.signal_aggregation.pipeline.pipeline import SignalAggregationPipeline
from backend.trade_validation_engine.signal_aggregation.stages.base import IAggregationStage
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult
from backend.trade_validation_engine.signal_aggregation.config.config import SignalAggregationConfig

class MockSuccessStage(IAggregationStage):
    @property
    def stage_id(self) -> str:
        return "MockSuccess"
        
    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        pipeline_state[self.stage_id] = "SuccessData"
        return AggregationStageResult(stage_id=self.stage_id, success=True)

class MockFailureStage(IAggregationStage):
    @property
    def stage_id(self) -> str:
        return "MockFailure"
        
    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        return AggregationStageResult(stage_id=self.stage_id, success=False, error_message="Failed")

class MockExceptionStage(IAggregationStage):
    @property
    def stage_id(self) -> str:
        return "MockException"
        
    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        raise ValueError("Crashed")

@pytest.fixture
def base_request():
    return SignalAggregationRequest(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        universe_snapshot_version=1, watchlist_snapshot_version=1,
        trend_snapshot_version=1, consolidation_snapshot_version=1,
        liquidity_grab_snapshot_version=1,
        configuration=SignalAggregationConfig(fail_fast=False)
    )

@pytest.mark.asyncio
async def test_pipeline_success(base_request):
    pipeline = SignalAggregationPipeline([MockSuccessStage(), MockSuccessStage()])
    success, results = await pipeline.execute(base_request)
    assert success is True
    assert len(results) == 2

@pytest.mark.asyncio
async def test_pipeline_fail_fast(base_request):
    req = base_request.model_copy(update={"configuration": SignalAggregationConfig(fail_fast=True)})
    pipeline = SignalAggregationPipeline([MockFailureStage(), MockSuccessStage()])
    success, results = await pipeline.execute(req)
    assert success is False
    assert len(results) == 1

@pytest.mark.asyncio
async def test_pipeline_no_fail_fast(base_request):
    pipeline = SignalAggregationPipeline([MockFailureStage(), MockSuccessStage()])
    success, results = await pipeline.execute(base_request)
    assert success is False
    assert len(results) == 2

@pytest.mark.asyncio
async def test_pipeline_exception_handling(base_request):
    pipeline = SignalAggregationPipeline([MockExceptionStage()])
    success, results = await pipeline.execute(base_request)
    assert success is False
    assert "Crashed" in results[0].error_message
