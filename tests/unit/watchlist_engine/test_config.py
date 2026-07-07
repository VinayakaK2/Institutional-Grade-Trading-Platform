"""
Unit tests for WatchlistSettings and sub-configuration models.

Covers:
  - Default values for all settings.
  - Composition of settings into WatchlistSettings.
  - Configuration fields are correctly typed and accessible.
"""
import pytest
from backend.watchlist_engine.models.config import (
    WatchlistPipelineSettings,
    WatchlistValidationSettings,
    WatchlistRepositorySettings,
    WatchlistSnapshotSettings,
    WatchlistSettings,
)


def test_pipeline_settings_defaults() -> None:
    """WatchlistPipelineSettings should have sensible production defaults."""
    settings = WatchlistPipelineSettings()
    assert settings.max_stages == 20
    assert settings.default_timeout_seconds == 300


def test_validation_settings_defaults() -> None:
    """WatchlistValidationSettings should disallow empty watchlists by default."""
    settings = WatchlistValidationSettings()
    assert settings.allow_empty_watchlist is False
    assert settings.max_watchlist_size == 500


def test_repository_settings_defaults() -> None:
    """WatchlistRepositorySettings should default max_snapshot_history to 100."""
    settings = WatchlistRepositorySettings()
    assert settings.max_snapshot_history == 100


def test_snapshot_settings_defaults() -> None:
    """WatchlistSnapshotSettings should default pipeline_version to '1.0.0'."""
    settings = WatchlistSnapshotSettings()
    assert settings.pipeline_version == "1.0.0"


def test_watchlist_settings_composes_all_sub_settings() -> None:
    """WatchlistSettings must expose all sub-settings as nested attributes."""
    settings = WatchlistSettings()
    assert isinstance(settings.pipeline, WatchlistPipelineSettings)
    assert isinstance(settings.validation, WatchlistValidationSettings)
    assert isinstance(settings.repository, WatchlistRepositorySettings)
    assert isinstance(settings.snapshot, WatchlistSnapshotSettings)


def test_watchlist_settings_custom_overrides() -> None:
    """WatchlistSettings should accept custom values for all nested settings."""
    settings = WatchlistSettings(
        pipeline=WatchlistPipelineSettings(max_stages=5, default_timeout_seconds=60),
        validation=WatchlistValidationSettings(allow_empty_watchlist=True, max_watchlist_size=100),
        repository=WatchlistRepositorySettings(max_snapshot_history=50),
        snapshot=WatchlistSnapshotSettings(pipeline_version="2.0.0"),
    )
    assert settings.pipeline.max_stages == 5
    assert settings.validation.allow_empty_watchlist is True
    assert settings.repository.max_snapshot_history == 50
    assert settings.snapshot.pipeline_version == "2.0.0"
