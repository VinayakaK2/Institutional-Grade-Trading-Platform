from abc import ABC, abstractmethod
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext

class IPaperExecutionQualityStage(ABC):
    """
    Contract for a deterministic stage in the paper execution quality pipeline.
    """
    @abstractmethod
    async def execute(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        pass
