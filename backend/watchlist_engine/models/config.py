"""
Watchlist Engine Configuration Models
======================================

Strongly-typed configuration models for the Watchlist Engine subsystem.

PIPELINE VERSION
----------------
`pipeline_version` in WatchlistSnapshotSettings is a semantic version string
that is stamped onto every WatchlistSnapshot produced by this configuration.

When to increment:
  - PATCH (e.g. 1.0.0 → 1.0.1): Bug fix in an existing stage without
    changing the stage's logical behaviour.
  - MINOR (e.g. 1.0.0 → 1.1.0): Add a new optional stage or change
    non-breaking stage configuration.
  - MAJOR (e.g. 1.0.0 → 2.0.0): Remove a stage, change the filtering
    contract, or fundamentally alter what symbols are included.
"""
from pydantic import Field
from backend.core.config import AppSettings


class WatchlistPipelineSettings(AppSettings):
    """Controls the structural behaviour of the WatchlistExecutionPipeline."""

    # Maximum number of registered stages. Prevents accidental pipeline bloat.
    max_stages: int = Field(
        default=20,
        description="Maximum number of watchlist pipeline stages allowed."
    )

    # Hard timeout for the entire pipeline run. Prevents runaway executions.
    default_timeout_seconds: int = Field(
        default=300,
        description="Default timeout in seconds for the entire watchlist pipeline."
    )


class WatchlistValidationSettings(AppSettings):
    """Controls structural validation rules applied to the candidate list."""

    # Set to True only in test environments where an empty list is acceptable.
    allow_empty_watchlist: bool = Field(
        default=False,
        description="Whether to allow an empty watchlist as a valid state. "
                    "Should be False in all production environments."
    )

    # Upper bound on watchlist size to prevent unbounded growth.
    max_watchlist_size: int = Field(
        default=500,
        description="Maximum number of candidates allowed in a single watchlist."
    )


class WatchlistRepositorySettings(AppSettings):
    """Controls repository behaviour for watchlist snapshot persistence."""

    # Maximum number of historical snapshots returned by list_snapshot_history().
    max_snapshot_history: int = Field(
        default=100,
        description="Maximum number of historical snapshots to retain for queries."
    )


class WatchlistSnapshotSettings(AppSettings):
    """Controls snapshot creation and versioning."""

    # Semantic version of the current watchlist pipeline definition.
    # MUST be incremented whenever pipeline stage logic changes.
    pipeline_version: str = Field(
        default="1.0.0",
        description="Semantic version of the watchlist pipeline configuration. "
                    "Stamped onto every generated WatchlistSnapshot."
    )


class WatchlistSettings(AppSettings):
    """
    Top-level configuration for the WatchlistEngine.

    All sub-component settings are composed here to provide a single
    configuration entry point for dependency injection.
    """

    # Pipeline structural configuration (stage limits, timeouts).
    pipeline: WatchlistPipelineSettings = Field(default_factory=WatchlistPipelineSettings)

    # Structural validation configuration (empty watchlists, size limits).
    validation: WatchlistValidationSettings = Field(default_factory=WatchlistValidationSettings)

    # Repository configuration (history limits).
    repository: WatchlistRepositorySettings = Field(default_factory=WatchlistRepositorySettings)

    # Snapshot configuration (pipeline versioning).
    snapshot: WatchlistSnapshotSettings = Field(default_factory=WatchlistSnapshotSettings)
