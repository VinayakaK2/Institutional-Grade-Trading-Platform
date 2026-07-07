import time
from typing import List
from backend.universe_engine.contracts.pipeline import IUniversePipeline, IUniverseStage
from backend.universe_engine.models.universe import UniverseExecutionContext, StageResult, StageStatus
from backend.core.logger import get_logger
from backend.universe_engine.models.exceptions import UniversePipelineError
from backend.universe_engine.models.config import PipelineSettings

logger = get_logger(__name__)

class UniverseExecutionPipeline(IUniversePipeline):
    def __init__(self, settings: PipelineSettings):
        self._stages: List[IUniverseStage] = []
        self._settings = settings

    def register_stage(self, stage: IUniverseStage) -> None:
        if len(self._stages) >= self._settings.max_stages:
            raise UniversePipelineError(f"Maximum pipeline stages ({self._settings.max_stages}) exceeded.")
        self._stages.append(stage)
        logger.debug(f"Registered universe pipeline stage: {stage.name}")

    async def execute(self, context: UniverseExecutionContext) -> UniverseExecutionContext:
        logger.info(f"Starting universe pipeline execution for run_id: {context.run_id}")
        
        for stage in self._stages:
            logger.info(f"Executing stage: {stage.name}")
            start_time = time.perf_counter()
            try:
                result = await stage.execute(context)
                
                # Validation: the stage must return a StageResult
                if not isinstance(result, StageResult):
                    raise UniversePipelineError(f"Stage {stage.name} did not return a StageResult.")
                    
                context.stage_results.append(result)
                
                if result.status == StageStatus.FAILED:
                    logger.error(f"Stage {stage.name} failed. Stopping pipeline.")
                    break
                    
            except Exception as e:
                duration = (time.perf_counter() - start_time) * 1000
                logger.error(f"Stage {stage.name} threw an unexpected exception.", exc_info=True)
                
                error_result = StageResult(
                    stage_name=stage.name,
                    status=StageStatus.FAILED,
                    duration_ms=duration,
                    warnings=[f"Unhandled exception: {str(e)}"]
                )
                context.stage_results.append(error_result)
                raise UniversePipelineError(f"Pipeline execution failed at stage {stage.name}", details={"error": str(e)}) from e

        logger.info(f"Finished universe pipeline execution. Stages run: {len(context.stage_results)}")
        return context
