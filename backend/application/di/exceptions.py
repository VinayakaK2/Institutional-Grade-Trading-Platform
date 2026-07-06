"""
Dependency Injection Exceptions
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class DependencyInjectionException(InfrastructureException):
    """Base exception for DI failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DI_ERROR"

class DependencyResolutionException(DependencyInjectionException):
    """Raised when a dependency cannot be resolved (e.g. not registered)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DI_RESOLUTION_ERROR"

class CircularDependencyException(DependencyInjectionException):
    """Raised when a circular dependency is detected during resolution."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DI_CIRCULAR_DEPENDENCY"
