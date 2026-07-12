import logging
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport
from backend.liquidity_grab_engine.quality.pipeline.stages import MetricEvaluationStage, QualityClassifierStage, ReportAssemblyStage
from backend.liquidity_grab_engine.quality.registry.registry import MetricRegistry
from backend.liquidity_grab_engine.quality.contracts.classifier import IQualityClassifier

logger = logging.getLogger(__name__)

class LiquidityGrabQualityPipeline:
    """
    Orchestrates the evaluation pipeline.
    """
    def __init__(self, metric_registry: MetricRegistry, classifier: IQualityClassifier):
        self.metric_stage = MetricEvaluationStage(metric_registry)
        self.classifier_stage = QualityClassifierStage(classifier)
        self.assembly_stage = ReportAssemblyStage()
        
    def execute(self, context: LiquidityGrabEvaluationContext) -> LiquidityGrabQualityReport:
        logger.info("Starting Liquidity Grab Quality Pipeline.")
        
        evidence = self.metric_stage.execute(context)
        classification = self.classifier_stage.execute(evidence, context)
        report = self.assembly_stage.execute(context, evidence, classification)
        
        logger.info(f"Quality pipeline finished for candidate {context.candidate.candidate_id}.")
        return report
