import time
from typing import List
from backend.portfolio_correlation_engine.contracts.pipeline import ICorrelationStage
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.exceptions import PortfolioCorrelationPipelineError

class PortfolioCorrelationPipeline:
    """
    Extensible execution framework supporting ordered execution of correlation assembly.
    """
    def __init__(self, stages: List[ICorrelationStage] = None):
        self._stages = stages or []
        
    async def execute(self, context: PortfolioCorrelationPipelineContext) -> PortfolioCorrelationPipelineContext:
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
                
        except PortfolioCorrelationPipelineError:
            raise
        except Exception as e:
            raise PortfolioCorrelationPipelineError(f"Pipeline execution failed: {str(e)}") from e
            
        return current_context
