class SignalAggregationError(Exception):
    """Base exception for Signal Aggregation Engine."""
    pass

class SnapshotNotFoundError(SignalAggregationError):
    """Raised when an upstream snapshot cannot be found."""
    pass

class AggregationPipelineError(SignalAggregationError):
    """Raised when the aggregation pipeline encounters an execution failure."""
    pass

class EvidenceAssemblyError(SignalAggregationError):
    """Raised when evidence cannot be successfully assembled."""
    pass

class RepositoryError(SignalAggregationError):
    """Raised for persistence layer failures."""
    pass

class InvalidAggregationRequestError(SignalAggregationError):
    """Raised when an invalid request is supplied."""
    pass
