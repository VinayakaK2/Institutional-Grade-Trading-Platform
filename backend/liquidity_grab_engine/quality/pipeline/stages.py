import logging
from backend.liquidity_grab_engine.quality.models.context import LiquidityGrabEvaluationContext
from backend.liquidity_grab_engine.quality.models.models import QualityEvidence, ClassificationSummary, LiquidityGrabQualityReport, EvaluationMetadata
from backend.liquidity_grab_engine.quality.registry.registry import MetricRegistry
from backend.liquidity_grab_engine.quality.contracts.classifier import IQualityClassifier

logger = logging.getLogger(__name__)

class MetricEvaluationStage:
    """
    Executes metrics from the registry to produce QualityEvidence.
    """
    def __init__(self, registry: MetricRegistry):
        self.registry = registry
        
    def execute(self, context: LiquidityGrabEvaluationContext) -> QualityEvidence:
        logger.info("Executing MetricEvaluationStage.")
        return self.registry.execute(context)

class QualityClassifierStage:
    """
    Executes the configured classifier against the evidence.
    """
    def __init__(self, classifier: IQualityClassifier):
        self.classifier = classifier
        
    def execute(self, evidence: QualityEvidence, context: LiquidityGrabEvaluationContext) -> ClassificationSummary:
        logger.info("Executing QualityClassifierStage.")
        return self.classifier.classify(evidence, context)

class ReportAssemblyStage:
    """
    Constructs the immutable LiquidityGrabQualityReport.
    """
    def execute(self, context: LiquidityGrabEvaluationContext, evidence: QualityEvidence, classification: ClassificationSummary) -> LiquidityGrabQualityReport:
        logger.info("Executing ReportAssemblyStage.")
        
        report_id = LiquidityGrabQualityReport.generate_id(
            candidate_id=context.candidate.candidate_id,
            dataset_version=context.dataset_version if hasattr(context, "dataset_version") else context.candidate.dataset_version,
            config_hash=context.configuration.generate_hash(),
            classifier_version=classification.classifier_algorithm_version
        )
        
        return LiquidityGrabQualityReport(
            report_id=report_id,
            candidate_id=context.candidate.candidate_id,
            symbol_id=context.candidate.symbol_id,
            timeframe=context.candidate.timeframe,
            dataset_version=context.candidate.dataset_version,
            parent_trend_snapshot_version=context.parent_trend_snapshot_version,
            parent_consolidation_snapshot_version=context.parent_consolidation_snapshot_version,
            configuration_hash=context.configuration.generate_hash(),
            evidence=evidence,
            classification=classification,
            metadata=EvaluationMetadata(
                pipeline_version=context.metadata.pipeline_version
            )
        )
