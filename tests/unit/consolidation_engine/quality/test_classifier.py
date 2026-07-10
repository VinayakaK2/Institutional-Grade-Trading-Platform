import pytest
from backend.consolidation_engine.quality.models import ConsolidationQualityMetrics, ConsolidationQualityLevel
from backend.consolidation_engine.quality.config import ConsolidationQualityConfiguration
from backend.consolidation_engine.quality.classifier import ConsolidationQualityClassifier

@pytest.fixture
def config():
    return ConsolidationQualityConfiguration(
        weight_range_stability=0.2,
        weight_boundary_respect=0.2,
        weight_price_containment=0.2,
        weight_candle_consistency=0.2,
        weight_range_symmetry=0.2,
        excellent_threshold=0.85,
        good_threshold=0.70,
        acceptable_threshold=0.50,
        poor_threshold=0.30
    )

def test_classifier_excellent(config):
    # Score 1.0
    metrics = ConsolidationQualityMetrics(
        range_stability=1.0, boundary_respect=1.0, price_containment=1.0,
        candle_consistency=1.0, range_symmetry=1.0, consolidation_duration=20
    )
    level = ConsolidationQualityClassifier.classify(metrics, config)
    assert level == ConsolidationQualityLevel.EXCELLENT

def test_classifier_good(config):
    # Score ~0.8
    metrics = ConsolidationQualityMetrics(
        range_stability=0.8, boundary_respect=0.8, price_containment=0.8,
        candle_consistency=0.8, range_symmetry=0.8, consolidation_duration=20
    )
    level = ConsolidationQualityClassifier.classify(metrics, config)
    assert level == ConsolidationQualityLevel.GOOD

def test_classifier_acceptable(config):
    # Score ~0.6
    metrics = ConsolidationQualityMetrics(
        range_stability=0.6, boundary_respect=0.6, price_containment=0.6,
        candle_consistency=0.6, range_symmetry=0.6, consolidation_duration=20
    )
    level = ConsolidationQualityClassifier.classify(metrics, config)
    assert level == ConsolidationQualityLevel.ACCEPTABLE

def test_classifier_poor(config):
    # Score ~0.4
    metrics = ConsolidationQualityMetrics(
        range_stability=0.4, boundary_respect=0.4, price_containment=0.4,
        candle_consistency=0.4, range_symmetry=0.4, consolidation_duration=20
    )
    level = ConsolidationQualityClassifier.classify(metrics, config)
    assert level == ConsolidationQualityLevel.POOR

def test_classifier_rejected(config):
    # Score ~0.2
    metrics = ConsolidationQualityMetrics(
        range_stability=0.2, boundary_respect=0.2, price_containment=0.2,
        candle_consistency=0.2, range_symmetry=0.2, consolidation_duration=20
    )
    level = ConsolidationQualityClassifier.classify(metrics, config)
    assert level == ConsolidationQualityLevel.REJECTED
