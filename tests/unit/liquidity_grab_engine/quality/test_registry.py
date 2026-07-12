import pytest
from unittest.mock import MagicMock
from backend.liquidity_grab_engine.quality.registry.registry import MetricRegistry
from backend.liquidity_grab_engine.quality.contracts.metrics import ISupportRecoveryMetric, IFalseBreakDepthMetric
from backend.liquidity_grab_engine.quality.models.models import MetricResult

def test_metric_registry_registration():
    registry = MetricRegistry()
    mock_metric = MagicMock(spec=ISupportRecoveryMetric)
    registry.register(mock_metric)
    
    metrics = registry.discover()
    assert len(metrics) == 1
    assert metrics[0] == mock_metric

def test_metric_registry_execution():
    registry = MetricRegistry()
    
    mock_support_metric = MagicMock(spec=ISupportRecoveryMetric)
    mock_support_metric.metric_id = "m1"
    mock_result_1 = MetricResult(metric_id="m1", metric_name="test1", normalized_score=0.8, metric_version="v1", execution_duration=0.1)
    mock_support_metric.evaluate.return_value = mock_result_1
    
    mock_depth_metric = MagicMock(spec=IFalseBreakDepthMetric)
    mock_depth_metric.metric_id = "m2"
    mock_result_2 = MetricResult(metric_id="m2", metric_name="test2", normalized_score=0.9, metric_version="v1", execution_duration=0.1)
    mock_depth_metric.evaluate.return_value = mock_result_2
    
    registry.register(mock_support_metric)
    registry.register(mock_depth_metric)
    
    mock_context = MagicMock()
    evidence = registry.execute(mock_context)
    
    assert evidence.support_recovery == mock_result_1
    assert evidence.false_break_depth == mock_result_2
    assert evidence.recovery_strength is None

def test_metric_registry_unrecognized_interface():
    registry = MetricRegistry()
    mock_metric = MagicMock() # Does not inherit from any specific IMetric sub-interface
    mock_metric.metric_id = "unknown"
    mock_metric.evaluate.return_value = MetricResult(metric_id="m", metric_name="test", normalized_score=1.0, metric_version="v1", execution_duration=0.1)
    
    registry.register(mock_metric)
    evidence = registry.execute(MagicMock())
    
    # Should ignore unrecognized metric and return empty evidence
    assert evidence.support_recovery is None

def test_metric_registry_execution_failure():
    registry = MetricRegistry()
    mock_metric = MagicMock(spec=ISupportRecoveryMetric)
    mock_metric.metric_id = "m1"
    mock_metric.evaluate.side_effect = Exception("Test error")
    
    registry.register(mock_metric)
    
    with pytest.raises(Exception, match="Test error"):
        registry.execute(MagicMock())

