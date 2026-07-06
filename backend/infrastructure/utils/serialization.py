"""
Shared Serialization Framework
Provides reusable serialization and deserialization utilities across all infrastructure services.
Defaults to JSON via Pydantic for strong typing and validation.
"""
import json
from typing import Any, Type, TypeVar, Optional, Dict, Union
from pydantic import BaseModel, ValidationError

from backend.core.exceptions import InfrastructureException
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class SerializationException(InfrastructureException):
    """Raised when serialization or deserialization fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "SERIALIZATION_ERROR"


class SerializationHelper:
    """Utility class for serializing and deserializing payloads."""

    @staticmethod
    def serialize_dict(data: dict) -> str:
        """Serializes a standard dictionary to JSON string."""
        try:
            return json.dumps(data)
        except TypeError as e:
            logger.error("Failed to serialize dictionary.", exc_info=True)
            raise SerializationException("Dictionary serialization failed.", {"error": str(e)}) from e

    @staticmethod
    def deserialize_dict(data: Union[str, bytes]) -> dict:
        """Deserializes a JSON string or bytes to a dictionary."""
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error("Failed to deserialize JSON to dictionary.", exc_info=True)
            raise SerializationException("Dictionary deserialization failed.", {"error": str(e)}) from e

    @staticmethod
    def serialize_model(model: BaseModel) -> str:
        """Serializes a Pydantic model to a JSON string."""
        try:
            return model.model_dump_json()
        except Exception as e:
            logger.error("Failed to serialize Pydantic model.", exc_info=True)
            raise SerializationException("Model serialization failed.", {"error": str(e)}) from e

    @staticmethod
    def deserialize_model(model_class: Type[T], data: Union[str, bytes]) -> T:
        """Deserializes a JSON string or bytes directly into a Pydantic model."""
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return model_class.model_validate_json(data)
        except ValidationError as e:
            logger.error(f"Failed to deserialize into {model_class.__name__}. Validation error.", exc_info=True)
            raise SerializationException("Model deserialization failed due to validation.", {"error": e.errors()}) from e
        except Exception as e:
            logger.error(f"Failed to deserialize into {model_class.__name__}.", exc_info=True)
            raise SerializationException("Model deserialization failed.", {"error": str(e)}) from e
