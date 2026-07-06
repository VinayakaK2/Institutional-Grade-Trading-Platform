from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.models.report import ValidationResult
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.symbol import SymbolReference

class ValidationContext:
    """
    Context passed to validation rules, allowing them to access metadata 
    and dependencies like the Market Calendar or Anomaly config.
    """
    def __init__(self, symbol: SymbolReference, timeframe: Timeframe, provider: str, dependencies: Dict[str, Any] = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.provider = provider
        self.dependencies = dependencies or {}

class ValidationRule(ABC):
    @abstractmethod
    async def validate(self, context: ValidationContext, records: List[RawCandle]) -> List[ValidationResult]:
        """
        Evaluate the records and return a list of findings (errors, warnings).
        """
        pass

class CleaningRule(ABC):
    @abstractmethod
    async def clean(self, records: List[RawCandle]) -> List[RawCandle]:
        """
        Applies cleaning operations.
        Returns the modified list of candles.
        """
        pass
