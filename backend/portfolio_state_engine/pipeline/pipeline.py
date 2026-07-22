import time
from typing import List
from backend.portfolio_state_engine.contracts.pipeline import IPortfolioStatePipelineStage
from backend.portfolio_state_engine.models.context import PortfolioStatePipelineContext
from backend.portfolio_state_engine.exceptions import PortfolioStatePipelineError

class PortfolioStatePipeline:
    """
    Extensible execution framework supporting ordered execution of portfolio state assembly.
    """
    def __init__(self, stages: List[IPortfolioStatePipelineStage] = None):
        self._stages = stages or []
        
    async def execute(self, context: PortfolioStatePipelineContext) -> PortfolioStatePipelineContext:
        current_context = context
        
        try:
            for stage in self._stages:
                stage_name = stage.__class__.__name__
                start_time = time.monotonic()
                
                current_context = await stage.execute(current_context)
                
                end_time = time.monotonic()
                
                new_timings = dict(current_context.stage_timings)
                new_timings[stage_name] = end_time - start_time
                current_context = current_context.model_copy(update={"stage_timings": new_timings})
                
        except PortfolioStatePipelineError:
            raise
        except Exception as e:
            raise PortfolioStatePipelineError(f"Pipeline execution failed: {str(e)}") from e
            
        return current_context
