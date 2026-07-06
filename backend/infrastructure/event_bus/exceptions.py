"""
Event Bus Exceptions
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class EventDispatchException(InfrastructureException):
    """Raised when an event fails to dispatch to its handlers."""
    def __init__(self, message: str = "Failed to dispatch event.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "EVENT_DISPATCH_ERROR"

class EventRegistrationException(InfrastructureException):
    """Raised when an event handler fails to register."""
    def __init__(self, message: str = "Failed to register event handler.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "EVENT_REGISTRATION_ERROR"
