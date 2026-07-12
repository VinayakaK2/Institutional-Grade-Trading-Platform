import logging
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext

logger = logging.getLogger(__name__)

class LifecycleStructuralValidator:
    def validate(self, context: LiquidityGrabLifecycleContext) -> None:
        logger.debug("Performing structural validation on Lifecycle Context")
        
        if context.candidate is None:
            raise ValueError("LiquidityGrabCandidate must not be None")
            
        if context.quality_report is None:
            raise ValueError("LiquidityGrabQualityReport must not be None")
            
        if context.evaluation_candles is None:
            raise ValueError("Evaluation candles must not be None")
            
        if context.configuration is None:
            raise ValueError("Configuration must not be None")
            
        if context.dataset_version is None or context.dataset_version <= 0:
            raise ValueError("Dataset version must be a positive integer")
