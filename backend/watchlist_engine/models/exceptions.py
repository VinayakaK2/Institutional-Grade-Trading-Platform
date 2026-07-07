"""
Watchlist Engine Exception Hierarchy
=====================================

Integrates with the Phase 0 PlatformException framework.
Each exception carries a unique error code and appropriate HTTP status code.
"""
from typing import Dict, Any, Optional
from backend.core.exceptions import PlatformException


class WatchlistConfigurationError(PlatformException):
    """Raised when watchlist configuration is invalid or missing."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="WATCHLIST_CONFIG_ERROR",
            status_code=500,
            details=details
        )


class WatchlistPipelineError(PlatformException):
    """Raised when the watchlist pipeline encounters an unrecoverable failure."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="WATCHLIST_PIPELINE_ERROR",
            status_code=500,
            details=details
        )


class WatchlistValidationError(PlatformException):
    """Raised when structural validation of watchlist candidates fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="WATCHLIST_VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class WatchlistRepositoryError(PlatformException):
    """Raised when a watchlist repository operation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="WATCHLIST_REPOSITORY_ERROR",
            status_code=500,
            details=details
        )


class WatchlistSnapshotError(PlatformException):
    """Raised when snapshot creation or persistence fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="WATCHLIST_SNAPSHOT_ERROR",
            status_code=500,
            details=details
        )
