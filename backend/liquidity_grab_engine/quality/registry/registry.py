import logging
from typing import List
from backend.liquidity_grab_engine.quality.contracts.metrics import (
    IMetric,
    ISupportRecoveryMetric,
    IRecoveryStrengthMetric,
    IRecoverySpeedMetric,
    IFalseBreakDepthMetric,
    IVolumeConfirmationMetric,
    IStructuralConsistencyMetric
)
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext
from backend.liquidity_grab_engine.quality.models.models import QualityEvidence

logger = logging.getLogger(__name__)

class MetricRegistry:
    """
    Registry for quality metrics. 
    Metrics are registered, discovered, and executed dynamically to preserve Open/Closed Principle.
    """
    def __init__(self):
        self._metrics: List[IMetric] = []

    def register(self, metric: IMetric) -> None:
        self._metrics.append(metric)

    def discover(self) -> List[IMetric]:
        return list(self._metrics)

    def execute(self, context: LiquidityGrabEvaluationContext) -> QualityEvidence:
        logger.info("Executing metrics via registry.")
        
        evidence_kwargs = {}
        
        # Sort by metric_id to guarantee deterministic execution order
        sorted_metrics = sorted(self._metrics, key=lambda m: m.metric_id)
        
        for metric in sorted_metrics:
            try:
                result = metric.evaluate(context)
                
                # Route the result to the correct field in QualityEvidence based on interface type
                if isinstance(metric, ISupportRecoveryMetric):
                    evidence_kwargs["support_recovery"] = result
                elif isinstance(metric, IRecoveryStrengthMetric):
                    evidence_kwargs["recovery_strength"] = result
                elif isinstance(metric, IRecoverySpeedMetric):
                    evidence_kwargs["recovery_speed"] = result
                elif isinstance(metric, IFalseBreakDepthMetric):
                    evidence_kwargs["false_break_depth"] = result
                elif isinstance(metric, IVolumeConfirmationMetric):
                    evidence_kwargs["volume_confirmation"] = result
                elif isinstance(metric, IStructuralConsistencyMetric):
                    evidence_kwargs["structural_consistency"] = result
                else:
                    logger.warning(f"Metric {metric.metric_id} interface not recognized by QualityEvidence.")
                    
            except Exception as e:
                logger.error(f"Metric {metric.metric_id} execution failed: {e}")
                raise
                
        return QualityEvidence(**evidence_kwargs)
