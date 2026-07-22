from abc import ABC, abstractmethod
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext

class IPaperOrderPipelineStage(ABC):
    """
    Contract for a deterministic stage in the paper order pipeline.
    """
    @abstractmethod
    async def execute(self, execution_context: PaperOrderExecutionContext, pipeline_context: PaperOrderPipelineContext) -> None:
        pass
