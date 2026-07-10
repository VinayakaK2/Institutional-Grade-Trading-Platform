
import pytest
from backend.consolidation_engine.models.fingerprint import BusinessFingerprint

def test_same_input_same_fingerprint():
    bf1 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )
    bf2 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )
    assert bf1.compute_hash() == bf2.compute_hash()

def test_different_config_different_fingerprint():
    bf1 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )
    bf2 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="def"
    )
    assert bf1.compute_hash() != bf2.compute_hash()

def test_different_input_different_fingerprint():
    bf1 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=1,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )
    bf2 = BusinessFingerprint(
        fingerprint_algorithm_version=1,
        parent_dataset_version=2,
        parent_trend_snapshot_version=1,
        pipeline_version="1.0",
        config_hash="abc"
    )
    assert bf1.compute_hash() != bf2.compute_hash()
