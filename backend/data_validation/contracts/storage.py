from typing import List, Protocol, runtime_checkable
from backend.historical_data.models.raw import RawCandle

@runtime_checkable
class QuarantineStorageContract(Protocol):
    """
    Interface for the quarantine persistence layer, 
    used for saving invalid records.
    """
    async def save_quarantined_candles(self, candles: List[RawCandle], reason: str = "Validation Failed") -> None:
        """Saves invalid raw footprints for audit and debug."""
        ...
