from abc import ABC, abstractmethod
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext

class IPaperFillPipelineStage(ABC):
    """
    Contract for a deterministic stage in the paper fill pipeline.
    """
    @abstractmethod
    async def execute(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext) -> None:
        pass
