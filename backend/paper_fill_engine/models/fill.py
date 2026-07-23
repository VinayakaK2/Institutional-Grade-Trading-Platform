from enum import Enum

class FillState(str, Enum):
    PENDING_FILL = "PENDING_FILL"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
