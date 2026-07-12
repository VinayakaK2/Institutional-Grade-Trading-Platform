import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.quality.pipeline.pipeline import LiquidityGrabQualityPipeline
from backend.liquidity_grab_engine.quality.models.models import QualityEvidence, ClassificationSummary, LiquidityGrabQualityEnum
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext

def test_liquidity_grab_quality_pipeline():
    mock_registry = MagicMock()
    mock_evidence = QualityEvidence()
    mock_registry.execute.return_value = mock_evidence
    
    mock_classifier = MagicMock()
    mock_classification = ClassificationSummary(
        quality=LiquidityGrabQualityEnum.GOOD,
        classifier_algorithm_version="v1",
        classifier_configuration_hash="hash"
    )
    mock_classifier.classify.return_value = mock_classification
    
    pipeline = LiquidityGrabQualityPipeline(mock_registry, mock_classifier)
    
    mock_context = MagicMock()
    mock_context.candidate = MagicMock()
    mock_context.candidate.candidate_id = "cand1"
    mock_context.candidate.symbol_id = "BTC"
    mock_context.candidate.timeframe = "H1"
    mock_context.candidate.dataset_version = 1
    mock_context.parent_trend_snapshot_version = 1
    mock_context.parent_consolidation_snapshot_version = 1
    mock_context.configuration.generate_hash.return_value = "config_hash"
    mock_context.metadata.pipeline_version = "v1.0"
    
    # Needs dataset_version on context or fallback to candidate
    mock_context.dataset_version = 1
    
    report = pipeline.execute(mock_context)
    
    assert report is not None
    assert report.candidate_id == "cand1"
    assert report.evidence == mock_evidence
    assert report.classification == mock_classification
    assert report.classification.quality == LiquidityGrabQualityEnum.GOOD
