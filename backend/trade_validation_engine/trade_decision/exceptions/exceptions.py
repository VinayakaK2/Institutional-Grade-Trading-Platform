class TradeDecisionError(Exception):
    """Base exception for all trade decision errors."""
    pass

class DecisionPipelineError(TradeDecisionError):
    """Raised when the decision pipeline fails due to infrastructure/configuration issues."""
    pass

class DecisionRepositoryError(TradeDecisionError):
    """Raised when repository operations fail."""
    pass

class DecisionBuilderError(TradeDecisionError):
    """Raised when builder fails to construct the snapshot."""
    pass
