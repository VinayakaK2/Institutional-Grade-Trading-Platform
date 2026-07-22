from typing import List
from backend.paper_execution_engine.contracts.pipeline import IPaperExecutionPipelineStage
from backend.paper_execution_engine.models.contexts import PaperExecutionContext, PaperExecutionPipelineContext

class PipelineExecutor:
    """
    Executes a sequence of registered pipeline stages.
    """
    
    def __init__(self, stages: List[IPaperExecutionPipelineStage] = None):
        self._stages = stages or []
        
    async def execute(self, execution_context: PaperExecutionContext, pipeline_context: PaperExecutionPipelineContext) -> None:
        """
        Executes registered stages in sequence. 
        For Phase 13.1, this operates with 0 stages.
        """
        for stage in self._stages:
            await stage.execute(execution_context, pipeline_context)
