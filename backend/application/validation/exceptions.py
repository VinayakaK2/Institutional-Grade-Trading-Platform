"""
Validation Exceptions
"""
from typing import Optional, List
from backend.core.exceptions import ValidationException

class BusinessValidationException(ValidationException):
    """Raised when a business/domain validation rule fails."""
    def __init__(self, message: str = "Business validation failed.", errors: Optional[List[str]] = None) -> None:
        details = {"errors": errors} if errors else {}
        super().__init__(message=message, details=details)
        self.error_code = "BUSINESS_VALIDATION_FAILED"
