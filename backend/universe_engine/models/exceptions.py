from backend.core.exceptions import PlatformException
from typing import Dict, Any, Optional

class UniverseConfigurationError(PlatformException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNIVERSE_CONFIG_ERROR", status_code=500, details=details)

class UniversePipelineError(PlatformException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNIVERSE_PIPELINE_ERROR", status_code=500, details=details)

class UniverseValidationError(PlatformException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNIVERSE_VALIDATION_ERROR", status_code=400, details=details)

class UniverseRepositoryError(PlatformException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNIVERSE_REPOSITORY_ERROR", status_code=500, details=details)

class UniverseProviderError(PlatformException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNIVERSE_PROVIDER_ERROR", status_code=502, details=details)
