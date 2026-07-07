from abc import ABC, abstractmethod
from typing import List
from backend.universe_engine.models.universe import UniverseInstrument

class IUniverseValidator(ABC):
    @abstractmethod
    def validate_symbols(self, instruments: List[UniverseInstrument]) -> None:
        """
        Perform structural validation on a raw list of instruments.
        Raises UniverseValidationError if validation fails.
        """
        pass
