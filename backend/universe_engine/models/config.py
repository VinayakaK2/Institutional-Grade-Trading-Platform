"""
Universe Engine Configuration Models
=====================================

Configuration models for the Universe Engine subsystem.

PIPELINE VERSION
----------------
`pipeline_version` in UniverseSettings is a semantic version string that is
stamped onto every UniverseSnapshot produced by this engine configuration.

When to increment:
  - PATCH (e.g. 1.0.0 → 1.0.1): Fix a bug in an existing stage without
    changing the stage's logical behaviour.
  - MINOR (e.g. 1.0.0 → 1.1.0): Add a new optional stage or change
    non-breaking stage configuration.
  - MAJOR (e.g. 1.0.0 → 2.0.0): Remove a stage, change the filtering
    contract, or fundamentally alter what symbols are included.

Incrementing the version is MANDATORY whenever the pipeline logic changes.
This ensures that snapshots remain traceable to the exact pipeline that
generated them.
"""
from pydantic import Field
from backend.core.config import AppSettings
from typing import List


class PipelineSettings(AppSettings):
    """Controls the structural behaviour of the UniverseExecutionPipeline."""

    # Maximum number of registered stages. Prevents accidental pipeline bloat.
    max_stages: int = Field(
        default=20,
        description="Maximum number of pipeline stages allowed."
    )

    # Hard timeout for the entire pipeline run. Prevents runaway executions.
    default_timeout_seconds: int = Field(
        default=300,
        description="Default timeout in seconds for the entire pipeline."
    )


class ValidationSettings(AppSettings):
    """Controls structural validation rules applied to the raw symbol list."""

    # Set to True only in test environments where an empty list is acceptable.
    allow_empty_universe: bool = Field(
        default=False,
        description="Whether to allow an empty universe as a valid state. "
                    "Should be False in all production environments."
    )

    # Enables strict format enforcement of symbol metadata fields.
    strict_metadata_validation: bool = Field(
        default=True,
        description="Enforce metadata format strictness."
    )


class UniverseSettings(AppSettings):
    """
    Top-level configuration for the UniverseEngine.

    All sub-component settings are composed here to provide a single
    configuration entry point for dependency injection.
    """

    # Pipeline structural configuration (stage limits, timeouts).
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)

    # Structural validation configuration (empty universes, duplicate rules).
    validation: ValidationSettings = Field(default_factory=ValidationSettings)

    # Ordered list of provider names to activate during universe generation.
    active_providers: List[str] = Field(
        default_factory=list,
        description="List of provider names to run during universe generation."
    )

    # Semantic version of the current pipeline definition.
    # This value is stamped onto every UniverseSnapshot for traceability.
    # MUST be incremented whenever pipeline stage logic changes.
    # Format: "<MAJOR>.<MINOR>.<PATCH>" — e.g. "1.0.0"
    pipeline_version: str = Field(
        default="1.0.0",
        description="Semantic version of the pipeline configuration. "
                    "Stamped onto every generated UniverseSnapshot."
    )
