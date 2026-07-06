"""
Metrics Instruments
Provides standard metric types: Counter, Gauge, Histogram, Timer.
"""
import time
from typing import List

class Metric:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class Counter(Metric):
    """A cumulative metric that represents a single monotonically increasing counter."""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._value = 0
        
    def inc(self, amount: int = 1) -> None:
        self._value += amount

    @property
    def value(self) -> int:
        return self._value

class Gauge(Metric):
    """A metric that represents a single numerical value that can arbitrarily go up and down."""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._value = 0.0
        
    def set(self, value: float) -> None:
        self._value = value
        
    def inc(self, amount: float = 1.0) -> None:
        self._value += amount
        
    def dec(self, amount: float = 1.0) -> None:
        self._value -= amount
        
    @property
    def value(self) -> float:
        return self._value

class Histogram(Metric):
    """Samples observations (like response sizes) and counts them in configurable buckets."""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._observations: List[float] = []
        
    def observe(self, value: float) -> None:
        self._observations.append(value)
        
    @property
    def count(self) -> int:
        return len(self._observations)
        
    @property
    def sum(self) -> float:
        return sum(self._observations)

class Timer:
    """Helper to record duration into a Histogram."""
    def __init__(self, histogram: Histogram):
        self._histogram = histogram
        self._start_time = None
        
    def __enter__(self):
        self._start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self._start_time
        self._histogram.observe(duration)
