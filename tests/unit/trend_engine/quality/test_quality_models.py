import pytest
from datetime import datetime, timezone

from backend.trend_engine.quality.models.models import (
    TrendStrengthResult,
    TrendConsistencyResult,
    PullbackQualityResult,
    TrendPersistenceResult,
    NormalizedQualityMetrics,
    TrendQualitySymbolResult,
    TrendQualityMetadata,
    TrendQualitySnapshot
)

def test_quality_models_immutability():
    """Verify that domain models are frozen and cannot be mutated."""
    strength = TrendStrengthResult(
        ema_separation_ratio=0.01,
        direction_stability_percent=100.0,
        is_extended=False
    )
    
    with pytest.raises(Exception): # Pydantic ValidationError for frozen model
        strength.ema_separation_ratio = 0.05

def test_quality_snapshot_creation():
    """Verify snapshot composition."""
    sym_result = TrendQualitySymbolResult(
        symbol_key="AAPL:NASDAQ",
        strength_metrics=TrendStrengthResult(ema_separation_ratio=0.02, direction_stability_percent=50.0, is_extended=False),
        consistency_metrics=TrendConsistencyResult(sequence_stability_ratio=1.0, structural_noise_percent=0.0, valid_structures_count=3),
        pullback_metrics=PullbackQualityResult(average_pullback_depth_percent=5.0, average_pullback_duration_bars=2.0, pullback_count=1, deepest_pullback_percent=5.0),
        persistence_metrics=TrendPersistenceResult(trend_age_bars=10, interruption_count=0, longest_uninterrupted_run_bars=10),
        normalized_metrics=NormalizedQualityMetrics(normalized_strength=0.4, normalized_consistency=1.0, normalized_pullback_quality=0.5, normalized_persistence=0.5)
    )
    
    metadata = TrendQualityMetadata(
        pipeline_version="1.0.0",
        configuration_hash="abc",
        configuration_version=1,
        quality_algorithm_version="1.0.0",
        evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        evaluation_duration_ms=10.0
    )
    
    snapshot = TrendQualitySnapshot(
        quality_snapshot_id="q_123",
        source_trend_snapshot_id="t_123",
        symbols=[sym_result],
        metadata=metadata
    )
    
    assert snapshot.quality_snapshot_id == "q_123"
    assert len(snapshot.symbols) == 1
    assert snapshot.symbols[0].symbol_key == "AAPL:NASDAQ"
