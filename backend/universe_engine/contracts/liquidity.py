from abc import ABC, abstractmethod
from typing import List, Optional

from backend.universe_engine.models.universe import UniverseInstrument
from backend.universe_engine.liquidity.models import LiquidityFilterContext, LiquidityQualifiedUniverse
from backend.market_data.models.candle import Candle

class ILiquidityDataProvider(ABC):
    """
    Contract for retrieving historical market data required for liquidity calculations.
    """
    @abstractmethod
    async def get_historical_candles(self, instrument: UniverseInstrument, lookback_days: int) -> List[Candle]:
        """
        Fetch OHLCV candles for the given lookback period (in daily resolution).
        """
        pass

class IFundamentalDataProvider(ABC):
    """
    Contract for retrieving fundamental data required for liquidity calculations.
    """
    @abstractmethod
    async def get_market_capitalization(self, instrument: UniverseInstrument) -> Optional[float]:
        """
        Fetch the current market capitalization for the instrument.
        """
        pass

class ILiquidityStage(ABC):
    """
    Contract for a single stage in the Liquidity Filter Pipeline.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the filtering stage."""
        pass

    @abstractmethod
    async def execute(
        self, 
        context: LiquidityFilterContext, 
        data_provider: ILiquidityDataProvider, 
        fundamental_provider: IFundamentalDataProvider
    ) -> None:
        """
        Executes the filter stage, updating the context in place.
        Instruments failing the criteria are moved from qualified_instruments
        to rejected_details with corresponding reasons.
        """
        pass

class ILiquidityRepository(ABC):
    """
    Contract for persisting and loading the LiquidityQualifiedUniverse.
    """
    @abstractmethod
    async def save_liquidity_universe(self, universe: LiquidityQualifiedUniverse) -> None:
        """Persist a new immutable liquidity universe."""
        pass

    @abstractmethod
    async def load_liquidity_universe(self, universe_id: str) -> Optional[LiquidityQualifiedUniverse]:
        """Load a liquidity universe by its ID."""
        pass
