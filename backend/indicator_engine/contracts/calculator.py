from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorType

class IndicatorCalculatorContract(ABC):
    """
    Contract for a mathematical indicator calculator.
    Must be pure and stateless.
    """
    
    @property
    @abstractmethod
    def indicator_type(self) -> IndicatorType:
        """Returns the type of indicator this calculator computes."""
        pass
        
    @abstractmethod
    def calculate(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_state: Dict[str, Any] = None,
        **kwargs
    ) -> List[IndicatorResult]:
        """
        Computes indicator values over a series of candles.
        
        Args:
            candles: Ascending chronological list of completed candles.
                     If previous_state is provided, this list only needs to contain 
                     the minimal required candles for the next calculation step.
            dataset_version: The version string of the dataset (e.g. RAW, v1).
            previous_state: Optional dictionary containing the last known indicator state.
            **kwargs: Calculator-specific parameters (e.g., period=14).
        """
        pass
