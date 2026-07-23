class PaperExecutionResultError(Exception):
    """Base exception for Paper Execution Result Engine"""
    pass

class PaperExecutionResultValidationError(PaperExecutionResultError):
    """Raised when upstream snapshots fail structural or consistency validation"""
    pass

class PaperExecutionResultCalculationError(PaperExecutionResultError):
    """Raised when engine stages fail to calculate status, summary, or timeline"""
    pass

class PaperExecutionResultPersistenceError(PaperExecutionResultError):
    """Raised when snapshot fails to save to or load from repository"""
    pass
