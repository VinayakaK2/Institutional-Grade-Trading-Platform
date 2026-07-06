"""
Instrument exceptions.
"""
from backend.core.exceptions import DomainException

class InstrumentException(DomainException):
    """Base exception for all instrument related errors."""
    pass

class DuplicateSymbolException(InstrumentException):
    """Raised when attempting to add a symbol that already exists in the registry."""
    def __init__(self, symbol: str, message: str = "Duplicate symbol"):
        super().__init__(f"{message}: {symbol}", error_code="DUPLICATE_SYMBOL")

class InvalidExchangeException(InstrumentException):
    """Raised when an exchange is invalid or unknown."""
    def __init__(self, exchange_code: str, message: str = "Invalid exchange"):
        super().__init__(f"{message}: {exchange_code}", error_code="INVALID_EXCHANGE")

class InvalidMetadataException(InstrumentException):
    """Raised when instrument metadata is malformed."""
    def __init__(self, details: str, message: str = "Invalid metadata"):
        super().__init__(f"{message}: {details}", error_code="INVALID_METADATA")

class RegistryLoadException(InstrumentException):
    """Raised when the registry fails to perform an initial load."""
    def __init__(self, details: str, message: str = "Registry load failure"):
        super().__init__(f"{message}: {details}", error_code="REGISTRY_LOAD_FAIL")

class RegistryUpdateException(InstrumentException):
    """Raised when the registry fails an incremental refresh."""
    def __init__(self, details: str, message: str = "Registry update failure"):
        super().__init__(f"{message}: {details}", error_code="REGISTRY_UPDATE_FAIL")

class InstrumentNotFoundException(InstrumentException):
    """Raised when looking up an instrument that does not exist."""
    def __init__(self, identifier: str, message: str = "Instrument not found"):
        super().__init__(f"{message}: {identifier}", error_code="INSTRUMENT_NOT_FOUND")

class InvalidSearchCriteriaException(InstrumentException):
    """Raised when a search query is malformed."""
    def __init__(self, details: str, message: str = "Invalid search criteria"):
        super().__init__(f"{message}: {details}", error_code="INVALID_SEARCH")
