from typing import List
from backend.trend_engine.lifecycle.contracts.contracts import ITrendLifecycleStage
from backend.trend_engine.lifecycle.pipeline.context import LifecycleExecutionContext

class TrendLifecyclePipeline:
    """
    Orchestrates the deterministic sequence of lifecycle evaluation stages.
    """
    def __init__(self, stages: List[ITrendLifecycleStage]):
        self._stages = stages

    async def execute(self, context: LifecycleExecutionContext) -> None:
        """
        Executes each stage sequentially.
        """
        for stage in self._stages:
            await stage.execute(context)
