"""
Trend Engine Pipeline
=====================

Manages ordered registration and sequential execution of Trend Engine stages.
Pipeline orchestration only. No business logic.
"""
import logging
from typing import List

from backend.trend_engine.contracts.contracts import ITrendPipeline, ITrendStage
from backend.trend_engine.pipeline.context import TrendExecutionContext

logger = logging.getLogger(__name__)


class TrendPipelineError(Exception):
    """Raised when the pipeline fails to execute a stage."""
    pass


class TrendPipeline(ITrendPipeline):
    """
    Executes ordered structural stages for the Trend Engine.
    """

    def __init__(self, fail_fast: bool = True):
        self._stages: List[ITrendStage] = []
        self._fail_fast = fail_fast

    def register_stage(self, stage: ITrendStage) -> None:
        """
        Registers a stage for execution. Stages are executed in the order registered.
        """
        self._stages.append(stage)

    async def execute(self, context: TrendExecutionContext) -> TrendExecutionContext:
        """
        Executes all registered stages in order.
        
        Args:
            context: The mutable TrendExecutionContext.
            
        Returns:
            The mutated context after all stages run.
        """
        logger.info(f"Starting pipeline execution. Run ID: {context.run_id}, Stages: {len(self._stages)}")
        
        for stage in self._stages:
            if context.is_cancelled:
                logger.warning(f"Pipeline cancelled. Halting execution before stage: {stage.name}")
                break

            logger.debug(f"Executing stage: {stage.name}")
            try:
                result = await stage.execute(context)
                context.stage_results.append(result)
                
                # Check for stage failure
                if result.status.name == "FAILED" and self._fail_fast:
                    msg = f"Pipeline failed at stage {stage.name}. Fail-fast enabled."
                    logger.error(msg)
                    raise TrendPipelineError(msg)
                    
            except Exception as e:
                msg = f"Unhandled exception in stage {stage.name}: {str(e)}"
                logger.exception(msg)
                if self._fail_fast:
                    raise TrendPipelineError(msg) from e
                
        logger.info(f"Pipeline execution completed. Run ID: {context.run_id}")
        return context
