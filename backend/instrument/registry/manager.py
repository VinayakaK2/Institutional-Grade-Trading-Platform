"""
Symbol Registry Manager
"""
import asyncio
from typing import Dict, List, Optional
from backend.instrument.contracts.registry import RegistryManagerContract, RegistrySnapshot
from backend.instrument.contracts.provider import SymbolProviderContract
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata
from backend.instrument.registry.versioning import VersionTracker, RegistrySnapshotModel
from backend.instrument.registry.validation import RegistryValidator
from backend.instrument.registry.loader import RegistryLoader
from backend.instrument.registry.refresher import RegistryRefresher
from backend.core.logger import get_logger

logger = get_logger("instrument.registry.manager")

class SymbolRegistryManager(RegistryManagerContract):
    """
    Maintains the active state of the registry.
    Orchestrates loads, refreshes, and versioning.
    """
    def __init__(self, providers: List[SymbolProviderContract]):
        self.providers = providers
        self.validator = RegistryValidator()
        self.loader = RegistryLoader(self.providers, self.validator)
        self.refresher = RegistryRefresher(self.providers, self.validator)
        self.version_tracker = VersionTracker()
        
        # Internal state
        self._exchanges: Dict[str, ExchangeMetadata] = {}
        self._instruments: Dict[str, Instrument] = {}
        self._lock = asyncio.Lock()
        
    async def get_instrument(self, internal_id: str) -> Optional[Instrument]:
        """Fetch a specific instrument by internal ID."""
        async with self._lock:
            return self._instruments.get(internal_id)
            
    async def get_exchange(self, code: str) -> Optional[ExchangeMetadata]:
        """Fetch a specific exchange by its code."""
        async with self._lock:
            return self._exchanges.get(code.upper())

    async def load_initial(self) -> None:
        """Performs a cold-boot load of the registry."""
        async with self._lock:
            exchanges_list, instruments_dict = await self.loader.load_all()
            
            # Map exchanges by code
            self._exchanges = {ex.code.upper(): ex for ex in exchanges_list}
            self._instruments = instruments_dict
            
            self.version_tracker.increment()
            logger.info(f"Registry initialized. Version: {self.version_tracker.current_version}")

    async def refresh_incremental(self) -> None:
        """Applies incremental updates to the active registry."""
        async with self._lock:
            if not self._instruments:
                logger.warning("Incremental refresh called but registry is empty. Performing initial load instead.")
                # We yield the lock and call load_initial (we must not hold the lock)
                pass # Handled outside the lock block
            else:
                current_ver_str = str(self.version_tracker.current_version)
                updated_instruments = await self.refresher.process_incremental(current_ver_str, self._instruments)
                self._instruments = updated_instruments
                self.version_tracker.increment()
                logger.info(f"Incremental refresh complete. Version: {self.version_tracker.current_version}")
                return
                
        # If we reached here, registry was empty
        await self.load_initial()

    async def refresh_full(self) -> None:
        """Re-runs the entire load process and hot-swaps the state."""
        # Load entirely off-lock to prevent blocking readers during the fetch
        exchanges_list, instruments_dict = await self.loader.load_all()
        
        async with self._lock:
            self._exchanges = {ex.code.upper(): ex for ex in exchanges_list}
            self._instruments = instruments_dict
            self.version_tracker.increment()
            logger.info(f"Full refresh complete. Version: {self.version_tracker.current_version}")

    def get_snapshot(self) -> RegistrySnapshot:
        """Returns an immutable snapshot of the current state."""
        return RegistrySnapshotModel(
            version=self.version_tracker.current_version,
            exchanges=list(self._exchanges.values()),
            instruments=list(self._instruments.values())
        )
