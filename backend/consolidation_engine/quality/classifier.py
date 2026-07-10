from backend.consolidation_engine.quality.models import ConsolidationQualityLevel, ConsolidationQualityMetrics
from backend.consolidation_engine.quality.config import ConsolidationQualityConfiguration

class ConsolidationQualityClassifier:
    """
    Combines metrics deterministically to produce a final quality level.
    This is the ONLY place where metrics are aggregated.
    
    Data Flow:
    Metric -> Normalized Score -> Config Weight -> Weighted Score -> Classifier
    
    The thresholds are applied in order to strictly enforce REJECTED > POOR > ACCEPTABLE > GOOD > EXCELLENT.
    """
    
    @staticmethod
    def classify(metrics: ConsolidationQualityMetrics, config: ConsolidationQualityConfiguration) -> ConsolidationQualityLevel:
        # Simple weighted sum for the 0-1 metrics
        score = (
            metrics.range_stability * config.weight_range_stability +
            metrics.boundary_respect * config.weight_boundary_respect +
            metrics.price_containment * config.weight_price_containment +
            metrics.candle_consistency * config.weight_candle_consistency +
            metrics.range_symmetry * config.weight_range_symmetry
        )
        
        # Add duration logic if weighted
        # In a real implementation this might be more nuanced
        # The prompt requires: REJECTED > POOR > ACCEPTABLE > GOOD > EXCELLENT precedence.
        # This implies we check bottom-up or top-down based on rules.
        
        # Simple threshold based classification
        if score < config.poor_threshold:
            return ConsolidationQualityLevel.REJECTED
        elif score < config.acceptable_threshold:
            return ConsolidationQualityLevel.POOR
        elif score < config.good_threshold:
            return ConsolidationQualityLevel.ACCEPTABLE
        elif score < config.excellent_threshold:
            return ConsolidationQualityLevel.GOOD
        else:
            return ConsolidationQualityLevel.EXCELLENT
