"""
Scheduler Exceptions
"""
from typing import Optional, Dict, Any
from backend.core.exceptions import InfrastructureException

class SchedulerException(InfrastructureException):
    """Raised when the scheduler encounters a critical failure."""
    def __init__(self, message: str = "Scheduler encountered an error.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "SCHEDULER_ERROR"

class JobExecutionException(InfrastructureException):
    """Raised when a scheduled job fails."""
    def __init__(self, message: str = "Scheduled job failed execution.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "JOB_EXECUTION_ERROR"
