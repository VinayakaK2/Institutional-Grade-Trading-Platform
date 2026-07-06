"""
Initial Registry Loader
"""
from typing import Dict, List, Tuple
from backend.instrument.contracts.provider import SymbolProviderContract
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.registry.validation import RegistryValidator
from backend.instrument.exceptions import RegistryLoadException
from backend.core.logger import get_logger

logger = get_logger("instrument.registry.loader")

class RegistryLoader:
    """
    Handles the initial cold-boot loading of the registry from providers.
    """
    def __init__(self, providers: List[SymbolProviderContract], validator: RegistryValidator):
        self.providers = providers
        self.validator = validator
        
    async def load_all(self) -> Tuple[List[ExchangeMetadata], Dict[str, Instrument]]:
        """
        Executes a full load from all registered providers.
        Returns validated exchanges and instruments.
        """
        logger.info(f"Starting initial registry load from {len(self.providers)} providers")
        
        all_exchanges: List[ExchangeMetadata] = []
        all_instruments: Dict[str, Instrument] = {}
        
        try:
            # 1. Load Exchanges
            for provider in self.providers:
                exchanges = await provider.fetch_exchanges()
                self.validator.validate_exchanges(exchanges)
                all_exchanges.extend(exchanges)
                
            # Cross-validate
            self.validator.set_active_exchanges(all_exchanges)
            
            # 2. Load Instruments
            for provider in self.providers:
                async for instrument_batch in provider.fetch_all_instruments():
                    self.validator.validate_instruments(
                        instrument_batch, 
                        existing_ids=set(all_instruments.keys())
                    )
                    
                    for instr in instrument_batch:
                        all_instruments[instr.identity.internal_id] = instr
                        
            logger.info(f"Initial load complete. {len(all_exchanges)} exchanges, {len(all_instruments)} instruments loaded.")
            return all_exchanges, all_instruments
            
        except Exception as e:
            logger.error(f"Failed to load registry: {str(e)}")
            raise RegistryLoadException(str(e)) from e
