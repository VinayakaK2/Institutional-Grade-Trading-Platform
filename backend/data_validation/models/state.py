from enum import Enum

class DataState(str, Enum):
    """
    Lifecycle state of historical data during certification.
    """
    UNVALIDATED = "UNVALIDATED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    CLEANING = "CLEANING"
    CLEANED = "CLEANED"
    CERTIFIED = "CERTIFIED"
    CANONICAL = "CANONICAL"
    QUARANTINED = "QUARANTINED"
