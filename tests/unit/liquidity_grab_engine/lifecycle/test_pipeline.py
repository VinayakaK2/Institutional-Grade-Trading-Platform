from unittest.mock import MagicMock
from backend.liquidity_grab_engine.lifecycle.pipeline.stages import EvidenceGenerationStage, LifecycleAggregatorStage, SnapshotAssemblyStage
from backend.liquidity_grab_engine.lifecycle.pipeline.pipeline import LiquidityGrabLifecyclePipeline
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot

def test_pipeline_execution():
    mock_evidence_stage = MagicMock(spec=EvidenceGenerationStage)
    mock_aggregator_stage = MagicMock(spec=LifecycleAggregatorStage)
    mock_assembly_stage = MagicMock(spec=SnapshotAssemblyStage)
    
    mock_snapshot = MagicMock(spec=LiquidityGrabLifecycleSnapshot)
    mock_snapshot.snapshot_id = "snap1"
    mock_assembly_stage.execute.return_value = mock_snapshot
    
    pipeline = LiquidityGrabLifecyclePipeline(mock_evidence_stage, mock_aggregator_stage, mock_assembly_stage)
    
    mock_context = MagicMock()
    mock_context.candidate.candidate_id = "c1"
    result = pipeline.execute(mock_context)
    
    assert result == mock_snapshot
    mock_evidence_stage.execute.assert_called_once_with(mock_context)
