from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class ICandleSeries(Protocol):
    """
    Protocol defining the required interface for market data candle series.
    The Detection Engine relies on this abstraction to isolate itself from
    data origin (Postgres, CSV, API, etc.).
    """
    
    def get_candles(self) -> Any:
        """Returns the underlying sequence of candles."""
        ...
        
    def __len__(self) -> int:
        """Returns the number of candles in the series."""
        ...
