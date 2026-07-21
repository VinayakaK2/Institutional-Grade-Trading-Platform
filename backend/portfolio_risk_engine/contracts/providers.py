import abc
from typing import Dict

class IPortfolioSnapshotProvider(abc.ABC):
    """
    Abstracts access to the current portfolio state.
    Provides necessary summaries to the Portfolio Risk Validation Engine.
    """
    
    @abc.abstractmethod
    def get_total_open_risk(self) -> float:
        """Returns the total open risk amount across all active trades."""
        pass
        
    @abc.abstractmethod
    def get_sector_exposure(self, sector: str) -> float:
        """Returns the current exposure (or risk) to a given sector."""
        pass
        
    @abc.abstractmethod
    def get_position_exposure(self, symbol: str) -> float:
        """Returns the current exposure to a specific symbol."""
        pass
        
    @abc.abstractmethod
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Returns a correlation matrix for current portfolio holdings."""
        pass
        
    @abc.abstractmethod
    def get_daily_risk(self) -> float:
        """Returns the accumulated loss/risk realized today."""
        pass
        
    @abc.abstractmethod
    def get_open_positions_count(self) -> int:
        """Returns the total number of open positions."""
        pass
