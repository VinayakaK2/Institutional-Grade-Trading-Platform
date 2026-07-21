from abc import ABC, abstractmethod
from typing import Optional, List
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot
from backend.risk_decision_engine.models.evidence import DecisionType

class IRiskDecisionQueryService(ABC):
    """
    Read-only query service for risk decisions.
    """
    @abstractmethod
    async def get_snapshot(self, snapshot_id: str) -> Optional[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def get_decisions_for_symbol(self, symbol: str) -> List[RiskDecisionSnapshot]:
        pass
        
    @abstractmethod
    async def get_decisions_by_type(self, decision: DecisionType) -> List[RiskDecisionSnapshot]:
        pass
