import abc
from typing import Dict
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.evidence import SizingEvidenceBase

class ISizingMetricStage(abc.ABC):
    """
    Contract for a sizing metric pipeline stage.
    """
    @property
    @abc.abstractmethod
    def stage_name(self) -> str:
        pass
        
    @abc.abstractmethod
    async def calculate(self, context: PositionSizingContext, previous_results: Dict[str, SizingEvidenceBase]) -> SizingEvidenceBase:
        """
        Executes the metric calculation and returns structured evidence.
        Accepts results from previous stages to allow evidence-driven sequential calculation.
        """
        pass
