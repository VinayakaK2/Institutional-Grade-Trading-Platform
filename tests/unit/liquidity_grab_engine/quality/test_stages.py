import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.quality.pipeline.stages import MetricEvaluationStage, QualityClassifierStage, ReportAssemblyStage
from backend.liquidity_grab_engine.quality.models.models import QualityEvidence, ClassificationSummary, LiquidityGrabQualityEnum

def test_metric_evaluation_stage():
    mock_registry = MagicMock()
    mock_evidence = QualityEvidence()
    mock_registry.execute.return_value = mock_evidence
    
    stage = MetricEvaluationStage(mock_registry)
    result = stage.execute(MagicMock())
    assert result == mock_evidence
    
def test_quality_classifier_stage():
    mock_classifier = MagicMock()
    mock_classification = ClassificationSummary(quality=LiquidityGrabQualityEnum.POOR, classifier_algorithm_version="v", classifier_configuration_hash="h")
    mock_classifier.classify.return_value = mock_classification
    
    stage = QualityClassifierStage(mock_classifier)
    result = stage.execute(QualityEvidence(), MagicMock())
    assert result == mock_classification
    
def test_report_assembly_stage():
    stage = ReportAssemblyStage()
    
    mock_context = MagicMock()
    mock_context.candidate.candidate_id = "c1"
    mock_context.candidate.symbol_id = "BTC"
    mock_context.candidate.timeframe = "H1"
    mock_context.candidate.dataset_version = 1
    mock_context.parent_trend_snapshot_version = 2
    mock_context.parent_consolidation_snapshot_version = 3
    mock_context.configuration.generate_hash.return_value = "config_hash"
    mock_context.metadata.pipeline_version = "v1"
    
    # Needs dataset_version on context or fallback to candidate
    mock_context.dataset_version = 1
    
    mock_evidence = QualityEvidence()
    mock_classification = ClassificationSummary(quality=LiquidityGrabQualityEnum.POOR, classifier_algorithm_version="v", classifier_configuration_hash="h")
    
    report = stage.execute(mock_context, mock_evidence, mock_classification)
    
    assert report.candidate_id == "c1"
    assert report.evidence == mock_evidence
    assert report.classification == mock_classification
    assert report.symbol_id == "BTC"
