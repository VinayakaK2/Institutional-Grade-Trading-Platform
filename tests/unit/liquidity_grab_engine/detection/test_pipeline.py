import pytest
import unittest.mock as mock
from backend.liquidity_grab_engine.detection.pipeline.pipeline import LiquidityGrabDetectionPipeline
from backend.liquidity_grab_engine.detection.pipeline.stages import (
    CandidateAssemblyStage, SupportBreakDetectionStage, RecoveryDetectionStage, FalseBreakValidationStage
)
from backend.liquidity_grab_engine.detection.contracts.strategies import (
    ISupportBreakDetectionStrategy, IRecoveryDetectionStrategy, IFalseBreakValidationStrategy
)
from backend.liquidity_grab_engine.detection.models.context import LiquidityGrabDetectionContext
from backend.liquidity_grab_engine.detection.models.models import DetectionEvidence, LiquidityGrabCandidate

def test_candidate_assembly_stage_success():
    context = mock.MagicMock()
    context.market_data.symbol.symbol = "AAPL"
    context.market_data.timeframe.value = "1h"
    context.dataset.version = 1
    context.parent_snapshots.trend_snapshot_version = 2
    context.parent_snapshots.consolidation_snapshot_version = 3
    context.configuration.generate_hash.return_value = "hash"
    context.metadata.pipeline_version = "1.0"
    
    evidence = DetectionEvidence(
        support_break_detected=True,
        recovery_detected=True,
        false_break_validated=True
    )
    
    stage = CandidateAssemblyStage()
    candidate = stage.execute(context, evidence)
    
    assert candidate is not None
    assert candidate.symbol_id == "AAPL"
    assert candidate.evidence.support_break_detected is True

def test_candidate_assembly_stage_incomplete():
    context = mock.MagicMock()
    evidence = DetectionEvidence(support_break_detected=True, recovery_detected=False)
    
    stage = CandidateAssemblyStage()
    candidate = stage.execute(context, evidence)
    assert candidate is None

def test_pipeline_execution():
    sb_strat = mock.Mock()
    sb_strat.detect.return_value = True
    
    rec_strat = mock.Mock()
    rec_strat.detect.return_value = True
    
    fb_strat = mock.Mock()
    fb_strat.validate.return_value = True
    
    stages = [
        SupportBreakDetectionStage(sb_strat),
        RecoveryDetectionStage(rec_strat),
        FalseBreakValidationStage(fb_strat)
    ]
    assembly = mock.MagicMock()
    assembly.execute.return_value = mock.MagicMock()
    
    pipeline = LiquidityGrabDetectionPipeline(stages, assembly)
    
    context = mock.MagicMock()
    context.configuration.pipeline.fail_fast = False
    
    candidate = pipeline.execute(context)
    assert candidate is not None

def test_pipeline_fail_fast():
    sb_strat = mock.Mock()
    sb_strat.detect.return_value = False
    
    rec_strat = mock.Mock()
    rec_strat.detect.return_value = True
    
    stages = [
        SupportBreakDetectionStage(sb_strat),
        RecoveryDetectionStage(rec_strat)
    ]
    assembly = mock.MagicMock()
    assembly.execute.return_value = None
    
    pipeline = LiquidityGrabDetectionPipeline(stages, assembly)
    
    context = mock.MagicMock()
    context.configuration.pipeline.fail_fast = True
    
    candidate = pipeline.execute(context)
    assert candidate is None
    rec_strat.detect.assert_not_called()

def test_pipeline_exception():
    sb_strat = mock.Mock()
    sb_strat.detect.side_effect = ValueError("Stage failed")
    
    pipeline = LiquidityGrabDetectionPipeline([SupportBreakDetectionStage(sb_strat)], mock.MagicMock())
    
    context = mock.MagicMock()
    with pytest.raises(ValueError, match="Stage failed"):
        pipeline.execute(context)
