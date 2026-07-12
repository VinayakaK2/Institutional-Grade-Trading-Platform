import pytest
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.liquidity_grab_engine.models.models import LiquidityGrabExecutionContext, LiquidityGrabSnapshot, LiquidityGrabConfigurationReference
from backend.liquidity_grab_engine.pipeline.stages import ILiquidityGrabStage
from backend.liquidity_grab_engine.pipeline.pipeline import LiquidityGrabPipeline

class MockStage(ILiquidityGrabStage):
    def execute(self, context, snapshot):
        return snapshot

class FailingStage(ILiquidityGrabStage):
    def execute(self, context, snapshot):
        raise ValueError("Stage failure")

import unittest.mock as mock

def test_empty_pipeline():
    context = mock.MagicMock(spec=LiquidityGrabExecutionContext)
    context.metadata = mock.MagicMock()
    context.metadata.pipeline_version = "1.0"
    
    snapshot = mock.MagicMock(spec=LiquidityGrabSnapshot)
    pipeline = LiquidityGrabPipeline(stages=[])
    
    result = pipeline.execute(context, snapshot)
    assert result == snapshot

def test_failing_stage():
    context = mock.MagicMock(spec=LiquidityGrabExecutionContext)
    context.metadata = mock.MagicMock()
    context.metadata.pipeline_version = "1.0"
    context.configuration = mock.MagicMock()
    context.configuration.pipeline.fail_fast = True
    
    snapshot = mock.MagicMock(spec=LiquidityGrabSnapshot)
    pipeline = LiquidityGrabPipeline(stages=[FailingStage()])
    
    with pytest.raises(ValueError, match="Stage failure"):
        pipeline.execute(context, snapshot)
