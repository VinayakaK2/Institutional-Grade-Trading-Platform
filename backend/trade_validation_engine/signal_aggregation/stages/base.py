from abc import ABC, abstractmethod
from typing import Dict, Any

from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationRequest, AggregationStageResult

class IAggregationStage(ABC):
    """
    Base contract for all Signal Aggregation pipeline stages.
    """
    
    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Returns the unique identifier for this stage."""
        pass

    @abstractmethod
    async def execute(self, request: SignalAggregationRequest, pipeline_state: Dict[str, Any]) -> AggregationStageResult:
        """
        Executes the aggregation logic, appending results or evidence to the stage result.
        The pipeline_state dict can be used to pass arbitrary intermediate data between stages if needed,
        although stages should primarily return evidence in AggregationStageResult.
        """
        pass
