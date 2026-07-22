from abc import ABC, abstractmethod
from typing import List, Optional
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot

class IPortfolioStateQueryService(ABC):
    """
    Projection-oriented read model interface.
    Answers historical and current state queries.
    """
    
    @abstractmethod
    async def get_latest_state(self) -> Optional[PortfolioStateSnapshot]:
        pass
        
    @abstractmethod
    async def get_history(self) -> List[PortfolioStateSnapshot]:
        pass
