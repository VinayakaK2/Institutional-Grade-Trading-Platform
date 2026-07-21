from abc import ABC, abstractmethod
from typing import Any
from backend.risk_optimization_engine.models.request import OptimizationRequest

class IRiskPipeline(ABC):
    """
    Abstraction over the business risk evaluation stages.
    The optimization engine must not know the internals of the pipeline.
    """
    
    @abstractmethod
    async def execute(self, request: OptimizationRequest) -> Any:
        """
        Executes the full risk pipeline and returns a RiskDecisionSnapshot (or similar business output).
        """
        pass
