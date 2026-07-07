"""
Freshness Engine Contracts
==========================

Read-only abstractions and repository interfaces for the Freshness Engine.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot
from backend.market_data.models.symbol import SymbolReference
from backend.market_data.models.timeframe import Timeframe
from backend.market_data.models.candle import Candle


class ICanonicalDatasetQueryService(ABC):
    """
    Read-only abstraction to discover the current certified dataset version.
    """
    @abstractmethod
    async def get_canonical_dataset_version(self, symbol: SymbolReference) -> str:
        """
        Retrieves the semantic version of the certified canonical dataset for the symbol.
        Raises an exception if no dataset exists or if it's not certified.
        """
        ...


class ICandleQueryService(ABC):
    """
    Read-only abstraction to fetch recent candles for structural and timestamp validation.
    """
    @abstractmethod
    async def get_latest_candles(
        self, 
        symbol: SymbolReference, 
        timeframe: Timeframe, 
        count: int
    ) -> List[Candle]:
        """
        Retrieves the most recent candles for the given symbol.
        """
        ...


class IFreshWatchlistRepository(ABC):
    """
    Contract for persisting and retrieving fresh watchlist snapshots.
    All write operations are INSERT-only. Existing snapshots must never be updated.
    """
    
    @abstractmethod
    async def save_fresh_snapshot(self, snapshot: FreshWatchlistSnapshot) -> None:
        """Persists a new fresh watchlist snapshot."""
        ...
        
    @abstractmethod
    async def load_latest_fresh_snapshot(self) -> Optional[FreshWatchlistSnapshot]:
        """Loads the most recently created fresh snapshot."""
        ...
        
    @abstractmethod
    async def load_fresh_snapshot_by_version(self, version: int) -> Optional[FreshWatchlistSnapshot]:
        """Loads a fresh snapshot by its exact version number."""
        ...
