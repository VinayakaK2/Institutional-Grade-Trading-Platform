import pytest
from datetime import datetime, timezone
import hashlib
from backend.liquidity_grab_engine.quality.models.models import (
    LiquidityGrabQualityEnum,
    MetricResult,
    QualityEvidence,
    ClassificationSummary,
    EvaluationMetadata,
    LiquidityGrabQualityReport
)

def test_metric_result_validation():
    result = MetricResult(
        metric_id="m1",
        metric_name="test",
        normalized_score=0.5,
        metric_version="v1",
        execution_duration=0.01,
        metadata={"raw": 100}
    )
    assert result.normalized_score == 0.5
    
    with pytest.raises(ValueError):
        MetricResult(
            metric_id="m1",
            metric_name="test",
            normalized_score=1.5, # Out of bounds
            metric_version="v1",
            execution_duration=0.01
        )

def test_quality_evidence_immutability():
    evidence = QualityEvidence()
    with pytest.raises(Exception):
        evidence.support_recovery = None

def test_classification_summary():
    summary = ClassificationSummary(
        quality=LiquidityGrabQualityEnum.EXCELLENT,
        classifier_algorithm_version="v1",
        classifier_configuration_hash="hash"
    )
    assert summary.quality == LiquidityGrabQualityEnum.EXCELLENT

def test_liquidity_grab_quality_report_id_generation():
    candidate_id = "cand1"
    dataset_version = 1
    config_hash = "conf_hash"
    classifier_version = "v1"
    
    expected_payload = f"{candidate_id}_{dataset_version}_{config_hash}_{classifier_version}"
    expected_hash = hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()
    
    generated_id = LiquidityGrabQualityReport.generate_id(candidate_id, dataset_version, config_hash, classifier_version)
    assert generated_id == expected_hash
