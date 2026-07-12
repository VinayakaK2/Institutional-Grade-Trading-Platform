import logging
from typing import Optional
from backend.liquidity_grab_engine.detection.models.context import LiquidityGrabDetectionContext
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate
from backend.liquidity_grab_engine.detection.pipeline.pipeline import LiquidityGrabDetectionPipeline
from backend.liquidity_grab_engine.detection.contracts.repository import ILiquidityGrabDetectionRepository
from backend.liquidity_grab_engine.detection.validation.structural import DetectionStructuralValidator
from backend.liquidity_grab_engine.detection.validation.consistency import DetectionConsistencyValidator

logger = logging.getLogger(__name__)

class LiquidityGrabDetectionEngine:
    """
    Thin orchestrator for Liquidity Grab Detection.
    Depends only on Detection Pipeline and Repository.
    Executes validation, delegates generation to the pipeline, and persists via repository.
    """
    
    def __init__(self, pipeline: LiquidityGrabDetectionPipeline, repository: ILiquidityGrabDetectionRepository):
        self.pipeline = pipeline
        self.repository = repository
        
    async def execute(self, context: LiquidityGrabDetectionContext) -> Optional[LiquidityGrabCandidate]:
        logger.info("LiquidityGrabDetectionEngine execution started.")
        
        try:
            # 1. Validation
            DetectionStructuralValidator.validate(context)
            DetectionConsistencyValidator.validate(context)
            
            # 2. Pipeline Execution
            candidate = self.pipeline.execute(context)
            
            # 3. Persistence
            if candidate:
                await self.repository.save(candidate)
                logger.info(f"Persisted candidate {candidate.candidate_id}.")
                
            return candidate
            
        except Exception as e:
            logger.error(f"Detection Engine failed: {str(e)}")
            raise
        finally:
            logger.info("LiquidityGrabDetectionEngine execution finished.")
