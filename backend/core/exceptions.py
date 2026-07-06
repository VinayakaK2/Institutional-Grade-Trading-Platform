"""
Exception Framework (Phase 0)
Provides a global exception architecture for the platform.
Defines base exceptions, categorized error types, and error codes.
"""
from typing import Any, Dict, Optional

class PlatformException(Exception):
    """Base exception for all expected platform errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the exception to a standard error response format."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


# --- Specific Exception Categories ---

class ValidationException(PlatformException):
    """Raised when input validation fails (e.g., bad API request)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            status_code=400,
            details=details
        )


class DomainException(PlatformException):
    """Raised when a core business rule is violated."""
    def __init__(self, message: str, error_code: str = "DOMAIN_RULE_VIOLATION", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=422,
            details=details
        )


class InfrastructureException(PlatformException):
    """Raised when external infrastructure fails (e.g., database down, broker API timeout)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="INFRASTRUCTURE_ERROR",
            status_code=503,
            details=details
        )


class AuthenticationException(PlatformException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details
        )


class AuthorizationException(PlatformException):
    """Raised when an authenticated user lacks permissions."""
    def __init__(self, message: str = "Permission denied.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=403,
            details=details
        )


class ConfigurationException(PlatformException):
    """Raised when the platform is misconfigured (e.g., missing env vars)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )
