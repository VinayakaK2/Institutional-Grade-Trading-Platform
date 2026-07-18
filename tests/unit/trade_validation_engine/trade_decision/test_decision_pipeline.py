import pytest
from backend.trade_validation_engine.trade_decision.pipeline.pipeline import TradeDecisionPipeline
from tests.unit.trade_validation_engine.trade_decision.conftest import MockValidStage, MockInvalidStage
from backend.trade_validation_engine.trade_decision.models.models import DecisionState

@pytest.mark.asyncio
async def test_pipeline_execution(valid_context, mock_validation_report):
    pipeline = TradeDecisionPipeline()
    pipeline.register_stage(MockValidStage())
    
    results = await pipeline.execute(valid_context, mock_validation_report)
    assert len(results) == 1
    assert results[0].state == DecisionState.VALID

@pytest.mark.asyncio
async def test_pipeline_fail_fast(valid_context, mock_validation_report):
    pipeline = TradeDecisionPipeline()
    pipeline.register_stage(MockInvalidStage())
    pipeline.register_stage(MockValidStage()) # Should not execute
    
    results = await pipeline.execute(valid_context, mock_validation_report)
    assert len(results) == 1
    assert results[0].state == DecisionState.INVALID

def test_pipeline_duplicate_stage_registration():
    from backend.trade_validation_engine.trade_decision.exceptions.exceptions import DecisionPipelineError
    pipeline = TradeDecisionPipeline()
    pipeline.register_stage(MockValidStage())
    with pytest.raises(DecisionPipelineError):
        pipeline.register_stage(MockValidStage())
