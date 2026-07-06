"""
Timeframe Model
"""
from enum import Enum

class Timeframe(str, Enum):
    """Standardized timeframes used across the platform."""
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

    def to_minutes(self) -> int:
        """Converts the timeframe to a minute representation."""
        mapping = {
            self.M1: 1,
            self.M3: 3,
            self.M5: 5,
            self.M15: 15,
            self.M30: 30,
            self.H1: 60,
            self.H2: 120,
            self.H4: 240,
            self.D1: 1440,
            self.W1: 10080,
            self.MN1: 43200, # Approx 30 days
        }
        return mapping[self]
