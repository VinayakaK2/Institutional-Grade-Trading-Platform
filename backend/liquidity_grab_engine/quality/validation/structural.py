import logging
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext

logger = logging.getLogger(__name__)

class QualityStructuralValidator:
    """
    Validates structural requirements of the context.
    """
    def validate(self, context: LiquidityGrabEvaluationContext) -> bool:
        if not context:
            logger.error("Context is missing.")
            return False
            
        if not context.candidate:
            logger.error("Candidate is missing.")
            return False
            
        if not context.candle_series:
            logger.error("Candle series is missing.")
            return False
            
        if not context.configuration:
            logger.error("Configuration is missing.")
            return False
            
        if not context.metadata:
            logger.error("Metadata is missing.")
            return False
            
        return True
