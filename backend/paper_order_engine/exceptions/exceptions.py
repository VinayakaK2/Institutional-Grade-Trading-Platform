class PaperOrderError(Exception):
    """Base exception for all Paper Order Engine errors."""
    pass

class PaperOrderValidationError(PaperOrderError):
    """Raised when an order fails structural validation."""
    pass

class PaperOrderConsistencyError(PaperOrderError):
    """Raised when an order fails consistency validation (e.g., missing parent snapshot)."""
    pass

class PaperOrderTransitionError(PaperOrderError):
    """Raised when an invalid state transition is attempted."""
    pass

class PaperOrderPersistenceError(PaperOrderError):
    """Raised when there is an issue persisting the snapshot."""
    pass
