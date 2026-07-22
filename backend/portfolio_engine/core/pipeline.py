import time
from typing import List
from backend.portfolio_engine.contracts.pipeline import IPortfolioPipelineStage
from backend.portfolio_engine.models.context import PortfolioPipelineContext
from backend.portfolio_engine.models.metadata import PipelineMetadata
from backend.portfolio_engine.exceptions import PortfolioPipelineError

class PortfolioPipeline:
    """
    Extensible execution framework supporting ordered execution and asynchronous stages.
    """
    def __init__(self, stages: List[IPortfolioPipelineStage] = None):
        self._stages = stages or []
        
    async def execute(self, context: PortfolioPipelineContext) -> PortfolioPipelineContext:
        current_context = context
        
        try:
            for stage in self._stages:
                stage_name = stage.__class__.__name__
                start_time = time.monotonic()
                
                # Execute the stage (business logic isolated to stages, which are empty in phase 12.1)
                current_context = await stage.execute(current_context)
                
                end_time = time.monotonic()
                # We do not mutate the immutable context directly; we would create a new one in real usage if we wanted to 
                # update the stage timings continuously. For this scaffold, we just collect it or rely on stages to return 
                # a new context with updated timings.
                # Actually, since it's immutable, we should instantiate a copy with updated timings.
                new_timings = dict(current_context.stage_timings)
                new_timings[stage_name] = end_time - start_time
                current_context = current_context.model_copy(update={"stage_timings": new_timings})
                
        except Exception as e:
            # Re-raise as a strongly typed pipeline infrastructure error
            raise PortfolioPipelineError(f"Pipeline execution failed: {str(e)}") from e
            
        # Post-execution metadata
        metadata = PipelineMetadata(
            pipeline_version=current_context.execution_context.configuration.pipeline_version,
            stage_count=len(self._stages),
            execution_mode="sequential"
        )
        
        return current_context.model_copy(update={"pipeline_metadata": metadata})
