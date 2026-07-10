import logging
from backend.consolidation_engine.quality.models import (
    ConsolidationEvaluationContext, 
    ConsolidationQualityMetrics, 
    ConsolidationQualityReport
)
from backend.consolidation_engine.quality.classifier import ConsolidationQualityClassifier
from backend.consolidation_engine.quality.metrics import (
    RangeStabilityMetric, BoundaryRespectMetric, PriceContainmentMetric,
    CandleConsistencyMetric, ConsolidationDurationMetric, RangeSymmetryMetric
)

logger = logging.getLogger(__name__)

class ConsolidationQualityEngine:
    """
    Orchestrates the independent metric evaluation and delegates to the classifier.
    Contains no business logic directly.
    """
    
    def __init__(self, algorithm_version: str = "1.0"):
        self.algorithm_version = algorithm_version
        self._metrics = {}
        
        # Register defaults
        self.register_metric("range_stability", RangeStabilityMetric())
        self.register_metric("boundary_respect", BoundaryRespectMetric())
        self.register_metric("price_containment", PriceContainmentMetric())
        self.register_metric("candle_consistency", CandleConsistencyMetric())
        self.register_metric("consolidation_duration", ConsolidationDurationMetric())
        self.register_metric("range_symmetry", RangeSymmetryMetric())
        
    def register_metric(self, name: str, metric) -> None:
        """Registers a metric dynamically for plug-and-play evaluation."""
        self._metrics[name] = metric
        
    def evaluate(self, context: ConsolidationEvaluationContext) -> ConsolidationQualityReport:
        logger.info(f"Quality evaluation start for candidate: {context.candidate.candidate_id}")
        
        try:
            # Independent Metric Evaluation
            m_rs = self._metrics["range_stability"].evaluate(context)
            m_br = self._metrics["boundary_respect"].evaluate(context)
            m_pc = self._metrics["price_containment"].evaluate(context)
            m_cc = self._metrics["candle_consistency"].evaluate(context)
            m_dur = self._metrics["consolidation_duration"].evaluate(context)
            m_sym = self._metrics["range_symmetry"].evaluate(context)
            
            metrics = ConsolidationQualityMetrics(
                range_stability=m_rs,
                boundary_respect=m_br,
                price_containment=m_pc,
                candle_consistency=m_cc,
                consolidation_duration=int(m_dur),
                range_symmetry=m_sym
            )
            
            # Classification
            level = ConsolidationQualityClassifier.classify(metrics, context.configuration)
            
            # Report Generation
            config_hash = context.configuration.compute_hash()
            report_id = ConsolidationQualityReport.generate_id(
                candidate_id=context.candidate.candidate_id,
                config_hash=config_hash,
                algorithm_version=self.algorithm_version
            )
            
            report = ConsolidationQualityReport(
                report_id=report_id,
                candidate_id=context.candidate.candidate_id,
                symbol=context.symbol,
                timeframe=context.timeframe,
                metrics=metrics,
                quality_level=level,
                config_version=context.configuration.config_version,
                algorithm_version=self.algorithm_version
            )
            
            logger.info(f"Quality evaluation finish for candidate: {context.candidate.candidate_id} - Level: {level.value}")
            return report
            
        except Exception as e:
            logger.error(f"Validation failure / Exception during quality evaluation: {str(e)}")
            raise
