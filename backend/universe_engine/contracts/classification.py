from abc import ABC, abstractmethod
from typing import Optional
from backend.universe_engine.models.universe import UniverseInstrument

class IClassificationDataProvider(ABC):
    """
    Contract for providing metadata required by the Universe Classification Engine.
    Must not include logic for fetching Phase 5.3 or Phase 5.4 statuses.
    """

    @abstractmethod
    async def get_sector(self, instrument: UniverseInstrument) -> Optional[str]:
        """Returns the sector name for the given instrument, or None if unknown."""
        pass

    @abstractmethod
    async def get_industry(self, instrument: UniverseInstrument) -> Optional[str]:
        """Returns the industry name for the given instrument, or None if unknown."""
        pass

    @abstractmethod
    async def get_market_cap(self, instrument: UniverseInstrument) -> Optional[float]:
        """Returns the market capitalization for the given instrument, or None if unknown."""
        pass


class IClassificationStage(ABC):
    """
    Contract for a single stage in the classification pipeline.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the classification stage."""
        pass

    @abstractmethod
    async def execute(self, context: 'UniverseClassificationContext', provider: IClassificationDataProvider) -> None: # type: ignore
        """Executes the classification stage logic."""
        pass


class IUniverseClassificationRepository(ABC):
    """
    Contract for persisting and retrieving ClassifiedUniverse snapshots.
    """
    @abstractmethod
    async def save_classified_universe(self, universe: 'ClassifiedUniverse') -> None: # type: ignore
        pass

    @abstractmethod
    async def load_classified_universe(self, universe_id: str) -> Optional['ClassifiedUniverse']: # type: ignore
        pass
