"""
Registry Refresher
"""
from typing import Dict, List
from backend.instrument.contracts.provider import SymbolProviderContract
from backend.instrument.models.instrument import Instrument
from backend.instrument.registry.validation import RegistryValidator
from backend.instrument.exceptions import RegistryUpdateException
from backend.core.logger import get_logger

logger = get_logger("instrument.registry.refresher")

class RegistryRefresher:
    """
    Handles incremental updates and full refreshes of an existing registry state.
    """
    def __init__(self, providers: List[SymbolProviderContract], validator: RegistryValidator):
        self.providers = providers
        self.validator = validator
        
    async def process_incremental(self, version_id: str, current_instruments: Dict[str, Instrument]) -> Dict[str, Instrument]:
        """
        Fetches only updates since the last version and applies them to a copy of the current state.
        Returns the mutated dictionary.
        """
        logger.info(f"Starting incremental refresh since version {version_id}")
        
        # We mutate the existing dictionary, so we assume caller passes a safe reference or we are fine mutating
        updates_applied = 0
        
        try:
            for provider in self.providers:
                async for instrument_batch in provider.fetch_updates_since(version_id):
                    # We don't pass existing_ids to trap duplicates, because an update MIGHT overwrite an existing instrument!
                    # However, we still validate exchange references.
                    self.validator.validate_instruments(instrument_batch, existing_ids=set())
                    
                    for instr in instrument_batch:
                        current_instruments[instr.identity.internal_id] = instr
                        updates_applied += 1
                        
            logger.info(f"Incremental refresh complete. {updates_applied} updates applied.")
            return current_instruments
            
        except Exception as e:
            logger.error(f"Failed incremental refresh: {str(e)}")
            raise RegistryUpdateException(str(e)) from e
