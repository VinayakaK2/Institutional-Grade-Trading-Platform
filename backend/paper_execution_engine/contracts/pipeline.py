from abc import ABC, abstractmethod
from backend.paper_execution_engine.models.contexts import PaperExecutionContext, PaperExecutionPipelineContext

class IPaperExecutionPipelineStage(ABC):
    """
    Interface for a paper execution pipeline stage.
    """
    
    @abstractmethod
    async def execute(self, execution_context: PaperExecutionContext, pipeline_context: PaperExecutionPipelineContext) -> None:
        """
        Executes the stage logic using the provided contexts.
        """
        pass
