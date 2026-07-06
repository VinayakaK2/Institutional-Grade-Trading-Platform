"""
Database Exceptions
Defines exceptions specific to database operations, inheriting from core exceptions.
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class DatabaseConnectionException(InfrastructureException):
    """Raised when the application fails to connect to the database."""
    def __init__(self, message: str = "Failed to connect to the database.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DATABASE_CONNECTION_ERROR"


class DatabaseTransactionException(InfrastructureException):
    """Raised when a database transaction fails (e.g., deadlock, serialization failure)."""
    def __init__(self, message: str = "Transaction failed.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DATABASE_TRANSACTION_ERROR"


class DatabaseIntegrityException(InfrastructureException):
    """Raised when a database integrity constraint is violated (e.g., unique violation, foreign key)."""
    def __init__(self, message: str = "Data integrity violation.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "DATABASE_INTEGRITY_ERROR"
        self.status_code = 409  # Conflict


class EntityNotFoundException(InfrastructureException):
    """Raised when an expected entity is not found in the database.
    Note: While conceptually related to the domain, it is often raised by the infra layer.
    """
    def __init__(self, entity_name: str, entity_id: Any) -> None:
        message = f"Entity '{entity_name}' with identifier '{entity_id}' was not found."
        super().__init__(message=message, details={"entity": entity_name, "id": str(entity_id)})
        self.error_code = "ENTITY_NOT_FOUND"
        self.status_code = 404
