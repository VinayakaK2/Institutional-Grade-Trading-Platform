import time
from typing import List
from backend.portfolio_exposure_engine.contracts.pipeline import IPortfolioExposurePipelineStage
from backend.portfolio_exposure_engine.models.contexts import PortfolioExposurePipelineContext
from backend.portfolio_exposure_engine.exceptions import PortfolioExposurePipelineError

class PortfolioExposurePipeline:
    """
    Extensible execution framework supporting ordered execution of portfolio exposure assembly.
    """
    def __init__(self, stages: List[IPortfolioExposurePipelineStage] = None):
        self._stages = stages or []
        
    async def execute(self, context: PortfolioExposurePipelineContext) -> PortfolioExposurePipelineContext:
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
                
        except PortfolioExposurePipelineError:
            raise
        except Exception as e:
            raise PortfolioExposurePipelineError(f"Pipeline execution failed: {str(e)}") from e
            
        return current_context
