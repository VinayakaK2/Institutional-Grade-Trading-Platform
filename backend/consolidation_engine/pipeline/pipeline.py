import time
import logging
from typing import List
from backend.consolidation_engine.models.models import ConsolidationExecutionContext, ConsolidationSnapshot
from backend.consolidation_engine.pipeline.stages.base import IConsolidationStage

logger = logging.getLogger(__name__)

class ConsolidationPipeline:
    """
    Executes a series of Consolidation Stages.
    Fail-fast, ordered execution with immutable context.
    """
    
    def __init__(self, stages: List["IConsolidationStage"]):
        self.stages = stages
        
    def execute(self, context: ConsolidationExecutionContext, snapshot: ConsolidationSnapshot) -> ConsolidationSnapshot:
        """
        Executes the pipeline stages on the given snapshot sequentially.
        """
        start_time = time.time()
        logger.info(f"ConsolidationPipeline {context.metadata.pipeline_version} Execution Started.")
        
        current_snapshot = snapshot
        
        for stage in self.stages:
            stage_name = stage.__class__.__name__
            logger.info(f"Pipeline Stage Started: {stage_name}")
            stage_start_time = time.time()
            
            try:
                current_snapshot = stage.execute(context, current_snapshot)
            except Exception as e:
                logger.error(f"Pipeline Stage {stage_name} failed: {str(e)}")
                raise
                
            stage_duration = time.time() - stage_start_time
            logger.info(f"Pipeline Stage Finished: {stage_name}. Duration: {stage_duration:.4f}s")
            
        total_duration = time.time() - start_time
        logger.info(f"ConsolidationPipeline Execution Finished. Total Duration: {total_duration:.4f}s")
        
        return current_snapshot
