from backend.trend_engine.optimization.models.models import BusinessFingerprint

def test_fingerprint_determinism():
    f1 = BusinessFingerprint(
        watchlist_snapshot_version=1,
        detection_algorithm_version="1.0",
        detection_config_hash="h1",
        quality_algorithm_version="1.0",
        quality_config_hash="h2",
        lifecycle_algorithm_version="1.0",
        lifecycle_rule_version=1,
        lifecycle_config_hash="h3",
        indicator_versions={"ema": "1.0", "atr": "1.1"}
    )
    
    f2 = BusinessFingerprint(
        watchlist_snapshot_version=1,
        detection_algorithm_version="1.0",
        detection_config_hash="h1",
        quality_algorithm_version="1.0",
        quality_config_hash="h2",
        lifecycle_algorithm_version="1.0",
        lifecycle_rule_version=1,
        lifecycle_config_hash="h3",
        indicator_versions={"atr": "1.1", "ema": "1.0"} # unordered dict
    )
    
    assert f1.compute_hash() == f2.compute_hash()

def test_fingerprint_changes_on_business_input():
    f1 = BusinessFingerprint(
        watchlist_snapshot_version=1,
        detection_algorithm_version="1.0",
        detection_config_hash="h1",
        quality_algorithm_version="1.0",
        quality_config_hash="h2",
        lifecycle_algorithm_version="1.0",
        lifecycle_rule_version=1,
        lifecycle_config_hash="h3",
        indicator_versions={"ema": "1.0"}
    )
    
    # Change config
    f2 = f1.model_copy(update={"quality_config_hash": "hx"})
    assert f1.compute_hash() != f2.compute_hash()
    
    # Change algo version
    f3 = f1.model_copy(update={"detection_algorithm_version": "1.1"})
    assert f1.compute_hash() != f3.compute_hash()
