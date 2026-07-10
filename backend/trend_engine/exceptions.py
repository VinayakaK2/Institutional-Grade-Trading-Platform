"""
Trend Engine Exceptions
=======================

Centralized exception hierarchy for the Trend Engine.
Inherits from the core infrastructure exception framework to ensure
consistent error handling across the platform.
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class TrendEngineException(InfrastructureException):
    """Base exception for all Trend Engine errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "TREND_ENGINE_ERROR"


class TrendRepositoryError(TrendEngineException):
    """Raised when the trend repository fails (e.g. duplicate insert)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "TREND_REPOSITORY_ERROR"


class DuplicateSnapshotVersionError(TrendRepositoryError):
    """Raised when attempting to save a snapshot with an existing ID or version."""
    def __init__(self, message: str = "Snapshot version already exists.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DUPLICATE_SNAPSHOT_VERSION_ERROR"
        self.status_code = 409


class MissingIndicatorDataError(TrendEngineException):
    """Raised when required indicator data (e.g. EMAs) is missing for a symbol."""
    def __init__(self, message: str = "Missing required indicator data.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "MISSING_INDICATOR_DATA_ERROR"
        self.status_code = 422


class MissingStructureDataError(TrendEngineException):
    """Raised when required market structure data is missing for a symbol."""
    def __init__(self, message: str = "Missing required market structure data.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "MISSING_STRUCTURE_DATA_ERROR"
        self.status_code = 422


class InvalidConfigurationError(TrendEngineException):
    """Raised when the pipeline or stage configuration is invalid."""
    def __init__(self, message: str = "Invalid configuration.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "INVALID_CONFIGURATION_ERROR"
        self.status_code = 400


class InvalidSnapshotLineageError(TrendEngineException):
    """Raised when the snapshot lineage is missing or inconsistent."""
    def __init__(self, message: str = "Invalid snapshot lineage.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "INVALID_SNAPSHOT_LINEAGE_ERROR"
        self.status_code = 400


class TrendPipelineExecutionError(TrendEngineException):
    """Raised when the trend detection pipeline encounters a critical failure."""
    def __init__(self, message: str = "Pipeline execution failed.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "TREND_PIPELINE_EXECUTION_ERROR"
