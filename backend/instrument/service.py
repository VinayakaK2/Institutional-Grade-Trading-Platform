"""
Symbol Registry Service (Facade)
"""
from typing import List, Optional
from backend.instrument.registry.manager import SymbolRegistryManager
from backend.instrument.search.index import SearchIndex
from backend.instrument.search.query import SearchQueryEngine
from backend.instrument.contracts.search import SearchCriteria
from backend.instrument.models.instrument import Instrument
from backend.core.logger import get_logger

logger = get_logger("instrument.service")

class SymbolRegistryService:
    """
    Primary facade for the rest of the application to access the Symbol Master & Instrument Registry.
    Combines the active state manager with the search engine.
    """
    def __init__(self, manager: SymbolRegistryManager):
        self.manager = manager
        self.index = SearchIndex()
        self.search_engine = SearchQueryEngine(self.index)
        
    async def initialize(self) -> None:
        """Boots the registry and builds the initial search index."""
        logger.info("Initializing Symbol Registry Service...")
        await self.manager.load_initial()
        self._rebuild_index()
        logger.info("Symbol Registry Service initialized.")

    async def refresh_incremental(self) -> None:
        """Polls providers for updates and patches the registry and index."""
        logger.info("Performing incremental registry refresh...")
        await self.manager.refresh_incremental()
        self._rebuild_index()
        
    async def refresh_full(self) -> None:
        """Completely rebuilds the registry and index from scratch."""
        logger.info("Performing full registry refresh...")
        await self.manager.refresh_full()
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Internal helper to rebuild search index from a snapshot."""
        snapshot = self.manager.get_snapshot()
        self.index.rebuild(snapshot.get_all_instruments())

    async def get_instrument(self, internal_id: str) -> Optional[Instrument]:
        """Fast lookup by internal ID."""
        return await self.manager.get_instrument(internal_id)

    def search(self, criteria: SearchCriteria) -> List[str]:
        """
        Executes a flexible search query. 
        Returns a list of internal IDs. 
        To get full objects, call `get_instrument` for each ID.
        """
        return self.search_engine.search(criteria)
