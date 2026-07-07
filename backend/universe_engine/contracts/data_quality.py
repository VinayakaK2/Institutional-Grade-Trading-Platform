from abc import ABC, abstractmethod
from typing import List, Optional, Set
from datetime import date

from backend.universe_engine.models.universe import UniverseInstrument
from backend.market_data.models.candle import Candle
from backend.universe_engine.data_quality.models import DataQualityFilterContext, CertifiedUniverse

class IDataQualityDataProvider(ABC):
    """
    Contract for retrieving historical market data required for data quality validation.
    Must return the Canonical Adjusted Dataset after the Corporate Actions Engine
    has successfully applied all approved adjustments.
    """
    @abstractmethod
    async def get_historical_candles(self, instrument: UniverseInstrument, lookback_days: int) -> List[Candle]:
        """
        Fetch OHLCV candles for the given lookback period (in daily resolution).
        """
        pass
    
    @abstractmethod
    async def get_dataset_version(self, instrument: UniverseInstrument) -> str:
        """
        Fetch the semantic version of the dataset currently being validated.
        Used to ensure consistency with the Corporate Actions Engine output.
        """
        pass

class IMarketCalendarProvider(ABC):
    """
    Contract for retrieving the official exchange trading calendar.
    Used to deterministically differentiate expected gaps (holidays, weekends) 
    from unexpected gaps (missing data).
    """
    @abstractmethod
    async def get_expected_trading_sessions(
        self, 
        instrument: UniverseInstrument, 
        start_date: date, 
        end_date: date
    ) -> Set[date]:
        """
        Returns a set of dates where trading was officially conducted for the instrument's exchange.
        """
        pass

class ICorporateActionProvider(ABC):
    """
    Contract for verifying that the Canonical Adjusted Dataset matches 
    the approved corporate actions.
    """
    @abstractmethod
    async def verify_adjustments_applied(
        self, 
        instrument: UniverseInstrument, 
        candles: List[Candle],
        dataset_version: str
    ) -> bool:
        """
        Verifies that all approved corporate actions (splits, dividends)
        have been correctly applied to the provided dataset and that the dataset
        version matches the Corporate Actions Engine output.
        Returns True if perfectly consistent.
        """
        pass

class IDataQualityStage(ABC):
    """
    Contract for a single stage in the Data Quality Filter Pipeline.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the filtering stage."""
        pass

    @abstractmethod
    async def execute(
        self, 
        context: DataQualityFilterContext, 
        data_provider: IDataQualityDataProvider,
        calendar_provider: IMarketCalendarProvider,
        corporate_action_provider: ICorporateActionProvider
    ) -> None:
        """
        Executes the filter stage, updating the context in place.
        Instruments failing the criteria are moved from certified_instruments
        to rejected_details.
        """
        pass

class IDataQualityRepository(ABC):
    """
    Contract for persisting and loading the CertifiedUniverse.
    """
    @abstractmethod
    async def save_certified_universe(self, universe: CertifiedUniverse) -> None:
        """Persist a new immutable certified universe."""
        pass

    @abstractmethod
    async def load_certified_universe(self, universe_id: str) -> Optional[CertifiedUniverse]:
        """Load a certified universe by its ID."""
        pass
