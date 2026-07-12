from unittest.mock import MagicMock
from backend.liquidity_grab_engine.lifecycle.pipeline.stages import EvidenceGenerationStage, LifecycleAggregatorStage, SnapshotAssemblyStage
from backend.liquidity_grab_engine.lifecycle.models.models import LifecycleSummary, LiquidityGrabLifecycleState, LifecycleEvidence

def test_evidence_generation_stage():
    mock_registry = MagicMock()
    mock_evidence = LifecycleEvidence()
    mock_registry.execute.return_value = mock_evidence
    
    stage = EvidenceGenerationStage(mock_registry)
    result = stage.execute(MagicMock())
    assert result == mock_evidence

def test_lifecycle_aggregator_stage():
    mock_aggregator = MagicMock()
    mock_summary = LifecycleSummary(state=LiquidityGrabLifecycleState.FAILED, aggregator_version="v")
    mock_aggregator.aggregate.return_value = mock_summary
    
    stage = LifecycleAggregatorStage(mock_aggregator)
    result = stage.execute(LifecycleEvidence())
    assert result == mock_summary

def test_snapshot_assembly_stage():
    stage = SnapshotAssemblyStage()
    mock_context = MagicMock()
    mock_context.candidate.candidate_id = "c1"
    mock_context.candidate.symbol_id = "BTC"
    mock_context.candidate.timeframe = "H1"
    mock_context.dataset_version = 1
    mock_context.configuration.generate_hash.return_value = "config_hash"
    mock_context.metadata.pipeline_version = "v1"
    mock_context.quality_report.report_id = "q1"
    
    evidence = LifecycleEvidence()
    summary = LifecycleSummary(state=LiquidityGrabLifecycleState.ACTIVE, aggregator_version="v1")
    
    snapshot = stage.execute(mock_context, evidence, summary)
    
    assert snapshot.candidate_id == "c1"
    assert snapshot.metadata["pipeline_version"] == "v1"
    assert snapshot.metadata["quality_report_id"] == "q1"
    assert snapshot.snapshot_id is not None
