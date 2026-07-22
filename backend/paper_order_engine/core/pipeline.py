from typing import List
from backend.paper_order_engine.contracts.pipeline import IPaperOrderPipelineStage
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext

class PipelineExecutor:
    """
    Executes a sequence of IPaperOrderPipelineStage instances deterministically.
    """
    def __init__(self, stages: List[IPaperOrderPipelineStage] = None):
        self._stages = stages or []

    async def execute(self, execution_context: PaperOrderExecutionContext, pipeline_context: PaperOrderPipelineContext) -> None:
        """
        Executes all stages in sequence.
        """
        for stage in self._stages:
            await stage.execute(execution_context, pipeline_context)
