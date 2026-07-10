"""
Trend Engine Configuration
==========================

Strongly typed configuration framework for the Trend Engine.

Provides validation, serialization, and deterministic configuration hashing.
Supports schema_version for future evolution without breaking lineage.
"""
import hashlib
import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any


class TrendPipelineSettings(BaseModel):
    """Configuration for Trend Engine pipeline execution."""
    model_config = ConfigDict(frozen=True)
    
    # Enables fail-fast execution in the pipeline.
    fail_fast: bool = True
    
    # Pipeline stages configuration overrides
    stage_overrides: Dict[str, Any] = Field(default_factory=dict)


class TrendValidationSettings(BaseModel):
    """Configuration for input and structural validation."""
    model_config = ConfigDict(frozen=True)
    
    # Maximum allowed symbols in a single execution.
    max_symbols: int = 10000


class TrendRepositorySettings(BaseModel):
    """Configuration for repository persistence."""
    model_config = ConfigDict(frozen=True)
    
    # Maximum history length returned by list_snapshot_history
    default_history_limit: int = 10


class TrendExecutionSettings(BaseModel):
    """Configuration for the execution context and environment."""
    model_config = ConfigDict(frozen=True)
    
    # Max execution time allowed per run
    timeout_ms: int = 30000


class TrendSettings(BaseModel):
    """
    Root configuration for the Trend Engine.

    Exposes deterministic configuration hashing and schema versioning.
    """
    model_config = ConfigDict(frozen=True)
    
    # Semantic version of the configuration schema.
    schema_version: str = "1.0.0"
    
    pipeline: TrendPipelineSettings = Field(default_factory=TrendPipelineSettings)
    validation: TrendValidationSettings = Field(default_factory=TrendValidationSettings)
    repository: TrendRepositorySettings = Field(default_factory=TrendRepositorySettings)
    execution: TrendExecutionSettings = Field(default_factory=TrendExecutionSettings)

    def generate_hash(self) -> str:
        """
        Generates a deterministic hash of the current configuration.

        This hash is used in snapshot lineage to prove that
        two executions used exactly the same configuration parameters.
        """
        config_dict = self.model_dump()
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_json.encode("utf-8")).hexdigest()
