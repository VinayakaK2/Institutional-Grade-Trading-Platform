import logging
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext

logger = logging.getLogger(__name__)

class QualityConsistencyValidator:
    """
    Validates consistency between context inputs.
    """
    def validate(self, context: LiquidityGrabEvaluationContext) -> bool:
        # Verify candidate lineages
        if context.candidate.parent_trend_snapshot_version != context.parent_trend_snapshot_version:
            logger.error("Parent Trend Snapshot version mismatch.")
            return False
            
        if context.candidate.parent_consolidation_snapshot_version != context.parent_consolidation_snapshot_version:
            logger.error("Parent Consolidation Snapshot version mismatch.")
            return False
            
        if context.candidate.configuration_hash != context.configuration.generate_hash():
            logger.error("Configuration hash mismatch.")
            return False
            
        return True
