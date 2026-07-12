import pytest
import asyncio
from backend.trade_validation_engine.models.context import TradeValidationExecutionContext
from backend.trade_validation_engine.config.config import TradeValidationConfig
from backend.trade_validation_engine.pipeline.pipeline import TradeValidationPipeline, IValidationStage
from backend.trade_validation_engine.models.models import ValidationStageResult

class MockSuccessStage(IValidationStage):
    @property
    def name(self) -> str:
        return "MockSuccess"
        
    def execute(self, context: TradeValidationExecutionContext) -> ValidationStageResult:
        return ValidationStageResult(stage_name=self.name, success=True)

class MockFailureStage(IValidationStage):
    @property
    def name(self) -> str:
        return "MockFailure"
        
    def execute(self, context: TradeValidationExecutionContext) -> ValidationStageResult:
        return ValidationStageResult(stage_name=self.name, success=False, error_message="Failed")

class MockExceptionStage(IValidationStage):
    @property
    def name(self) -> str:
        return "MockException"
        
    def execute(self, context: TradeValidationExecutionContext) -> ValidationStageResult:
        raise ValueError("Something crashed")

def test_pipeline_success():
    pipeline = TradeValidationPipeline(stages=[MockSuccessStage(), MockSuccessStage()])
    context = TradeValidationExecutionContext(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig()
    )
    result = pipeline.execute(context)
    assert result.success is True
    assert len(result.stage_results) == 2

def test_pipeline_fail_fast():
    pipeline = TradeValidationPipeline(stages=[MockFailureStage(), MockSuccessStage()])
    context = TradeValidationExecutionContext(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig(fail_fast=True)
    )
    result = pipeline.execute(context)
    assert result.success is False
    assert len(result.stage_results) == 1  # Should halt after the first failure

def test_pipeline_no_fail_fast():
    pipeline = TradeValidationPipeline(stages=[MockFailureStage(), MockSuccessStage()])
    context = TradeValidationExecutionContext(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig(fail_fast=False)
    )
    result = pipeline.execute(context)
    assert result.success is False
    assert len(result.stage_results) == 2  # Should execute both despite failure

def test_pipeline_exception_handling():
    pipeline = TradeValidationPipeline(stages=[MockExceptionStage(), MockSuccessStage()])
    context = TradeValidationExecutionContext(
        symbol="BTCUSD", timeframe="1H", dataset_version=1,
        parent_watchlist_snapshot_version=1, parent_trend_snapshot_version=1,
        parent_consolidation_snapshot_version=1, parent_liquidity_grab_snapshot_version=1,
        configuration=TradeValidationConfig(fail_fast=True)
    )
    result = pipeline.execute(context)
    assert result.success is False
    assert len(result.stage_results) == 1
    assert "Unhandled exception during execution: Something crashed" in result.stage_results[0].error_message
