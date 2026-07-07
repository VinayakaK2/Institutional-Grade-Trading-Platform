from typing import List
from backend.universe_engine.contracts.validator import IUniverseValidator
from backend.universe_engine.models.exceptions import UniverseValidationError
from backend.universe_engine.models.config import ValidationSettings
from backend.universe_engine.models.universe import UniverseInstrument
from backend.core.logger import get_logger

logger = get_logger(__name__)

class UniverseValidator(IUniverseValidator):
    """
    Default structural validator for Universe Engine.
    Enforces rules:
      - Universe must not be empty (unless configured otherwise).
      - Instruments cannot be None.
      - Instrument full_name (exchange:symbol) must be strictly unique.
    """
    def __init__(self, settings: ValidationSettings):
        self._settings = settings

    def validate_symbols(self, instruments: List[UniverseInstrument]) -> None:
        if not instruments and not self._settings.allow_empty_universe:
            raise UniverseValidationError("Universe is empty, but allow_empty_universe is False.")
            
        seen_tickers = set()
        
        for idx, inst in enumerate(instruments):
            if inst is None:
                raise UniverseValidationError(f"Null instrument encountered at index {idx}.")
                
            ticker = inst.symbol.symbol
            
            if not ticker or not ticker.strip():
                raise UniverseValidationError(f"Whitespace or empty ticker encountered at index {idx}.")
                
            full_name = inst.symbol.full_name
            if full_name in seen_tickers:
                raise UniverseValidationError(f"Duplicate symbol detected: {full_name}")
                
            seen_tickers.add(full_name)
            
        logger.debug(f"Universe validation passed for {len(instruments)} instruments.")
