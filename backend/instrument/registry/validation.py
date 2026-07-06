"""
Registry Validation Engine
"""
from typing import List, Set
from backend.instrument.models.instrument import Instrument, InstrumentStatus
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.exceptions import (
    DuplicateSymbolException,
    InvalidExchangeException,
    InvalidMetadataException
)
from backend.core.logger import get_logger

logger = get_logger("instrument.registry.validation")

class RegistryValidator:
    """
    Validates instruments and exchanges before they are committed to the registry.
    """
    def __init__(self):
        # We hold valid exchange codes during a validation session
        self.valid_exchanges: Set[str] = set()
        
    def set_active_exchanges(self, exchanges: List[ExchangeMetadata]) -> None:
        """Updates the known valid exchanges for cross-validation."""
        self.valid_exchanges = {ex.code.upper() for ex in exchanges}

    def validate_exchanges(self, exchanges: List[ExchangeMetadata]) -> None:
        """Validates a batch of exchanges."""
        seen_codes = set()
        for ex in exchanges:
            code = ex.code.upper()
            if code in seen_codes:
                logger.error(f"Duplicate exchange code detected: {code}")
                raise InvalidExchangeException(code, "Duplicate exchange code in batch")
            seen_codes.add(code)

    def validate_instruments(self, instruments: List[Instrument], existing_ids: Set[str] = None) -> None:
        """
        Validates a batch of instruments.
        Ensures exchanges are known, metadata is sane, and traps duplicates.
        """
        if existing_ids is None:
            existing_ids = set()
            
        seen_in_batch: Set[str] = set()
        
        for instr in instruments:
            iid = instr.identity.internal_id
            
            # 1. Duplicate check
            if iid in existing_ids:
                logger.error(f"Duplicate instrument internal_id in registry: {iid}")
                raise DuplicateSymbolException(iid, "Instrument already exists in registry")
            
            if iid in seen_in_batch:
                logger.error(f"Duplicate instrument internal_id in batch: {iid}")
                raise DuplicateSymbolException(iid, "Duplicate instrument in update batch")
                
            seen_in_batch.add(iid)
            
            # 2. Exchange Check
            ex_code = instr.identity.exchange.upper()
            if ex_code not in self.valid_exchanges:
                logger.error(f"Instrument {iid} references unknown exchange: {ex_code}")
                raise InvalidExchangeException(ex_code, f"Unknown exchange for instrument {iid}")
                
            # 3. Warning on Delisted
            if instr.metadata.status == InstrumentStatus.DELISTED:
                logger.warning(f"Instrument is marked as DELISTED: {iid}")
                
            # 4. Strict Metadata limits
            if instr.metadata.tick_size <= 0:
                raise InvalidMetadataException(f"{iid} tick_size", "Tick size must be positive")
                
            if instr.metadata.lot_size <= 0:
                raise InvalidMetadataException(f"{iid} lot_size", "Lot size must be positive")
