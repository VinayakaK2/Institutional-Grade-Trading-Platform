class TrendLifecycleError(Exception):
    """Base exception for Trend Lifecycle Engine."""
    pass

class InvalidLifecycleTransitionError(TrendLifecycleError):
    """Raised when an invalid lifecycle state transition is attempted."""
    pass

class MissingSnapshotError(TrendLifecycleError):
    """Raised when a required parent snapshot is missing."""
    pass

class LifecycleEvaluationError(TrendLifecycleError):
    """Raised when a lifecycle evaluation stage fails."""
    pass

class InvalidLifecycleStateError(TrendLifecycleError):
    """Raised when an unrecognized lifecycle state is encountered."""
    pass
