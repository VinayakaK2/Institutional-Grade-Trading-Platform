import time
import logging
from typing import List
from backend.liquidity_grab_engine.models.models import LiquidityGrabExecutionContext, LiquidityGrabSnapshot
from backend.liquidity_grab_engine.pipeline.stages import ILiquidityGrabStage

logger = logging.getLogger(__name__)

class LiquidityGrabPipeline:
    """
    Executes a series of Liquidity Grab Stages.
    Ordered, fail-fast execution with empty-state grace.
    """
    
    def __init__(self, stages: List[ILiquidityGrabStage]):
        self.stages = stages
        
    def execute(self, context: LiquidityGrabExecutionContext, snapshot: LiquidityGrabSnapshot) -> LiquidityGrabSnapshot:
        start_time = time.time()
        logger.info(f"LiquidityGrabPipeline {context.metadata.pipeline_version} Execution Started.")
        
        current_snapshot = snapshot
        
        if not self.stages:
            logger.info("LiquidityGrabPipeline has no registered stages (Phase 9.1). Returning snapshot unmodified.")
            total_duration = time.time() - start_time
            logger.info(f"LiquidityGrabPipeline Execution Finished. Total Duration: {total_duration:.4f}s")
            return current_snapshot
        
        for stage in self.stages:
            stage_name = stage.__class__.__name__
            logger.info(f"Pipeline Stage Started: {stage_name}")
            stage_start_time = time.time()
            
            try:
                current_snapshot = stage.execute(context, current_snapshot)
            except Exception as e:
                logger.error(f"Pipeline Stage {stage_name} failed: {str(e)}")
                if context.configuration.pipeline.fail_fast:
                    raise
                
            stage_duration = time.time() - stage_start_time
            logger.info(f"Pipeline Stage Finished: {stage_name}. Duration: {stage_duration:.4f}s")
            
        total_duration = time.time() - start_time
        logger.info(f"LiquidityGrabPipeline Execution Finished. Total Duration: {total_duration:.4f}s")
        
        return current_snapshot
