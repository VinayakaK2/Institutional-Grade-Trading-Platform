from abc import ABC, abstractmethod
from typing import List, Optional
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot

class IPortfolioCorrelationQueryService(ABC):
    """
    Projection-oriented read-only service for Portfolio Correlation.
    """
    
    @abstractmethod
    async def get_latest_correlation(self) -> Optional[PortfolioCorrelationSnapshot]:
        pass
        
    @abstractmethod
    async def get_history(self) -> List[PortfolioCorrelationSnapshot]:
        pass
        
    @abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[PortfolioCorrelationSnapshot]:
        pass
