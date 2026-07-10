import logging
from typing import List
from backend.consolidation_engine.lifecycle.models import (
    ConsolidationLifecycleContext,
    ConsolidationLifecycleSnapshot,
    BaseLifecycleEvidence
)
from backend.consolidation_engine.lifecycle.evidence import (
    ILifecycleEvidenceEvaluator,
    ContinuationEvidenceEvaluator,
    WeakeningEvidenceEvaluator,
    BreakEvidenceEvaluator,
    EndEvidenceEvaluator
)
from backend.consolidation_engine.lifecycle.aggregator import LifecycleAggregator

logger = logging.getLogger(__name__)

class ConsolidationLifecycleEngine:
    """
    Orchestrates independent evidence evaluators and delegates to the aggregator.
    Stateless engine producing immutable snapshots.
    """
    
    def __init__(self, algorithm_version: str = "1.0", rule_version: str = "1.0"):
        self.algorithm_version = algorithm_version
        self.rule_version = rule_version
        
        self._evaluators: List[ILifecycleEvidenceEvaluator] = [
            EndEvidenceEvaluator(),
            BreakEvidenceEvaluator(),
            WeakeningEvidenceEvaluator(),
            ContinuationEvidenceEvaluator()
        ]
        
    def evaluate(self, context: ConsolidationLifecycleContext) -> ConsolidationLifecycleSnapshot:
        logger.info(f"Lifecycle evaluation start for candidate: {context.candidate.candidate_id}")
        
        try:
            # 1. Gather Evidence
            evidence_list: List[BaseLifecycleEvidence] = []
            for evaluator in self._evaluators:
                logger.debug(f"Evaluating evidence stage: {type(evaluator).__name__}")
                evidence = evaluator.evaluate(context)
                evidence_list.append(evidence)
                
            # 2. Aggregation & Resolution
            final_state = LifecycleAggregator.resolve_state(evidence_list, context.configuration)
            logger.info(f"Lifecycle resolution: {final_state.value}")
            
            # 3. Snapshot Generation
            config_hash = context.configuration.compute_hash()
            snapshot_id = ConsolidationLifecycleSnapshot.generate_id(
                candidate_id=context.candidate.candidate_id,
                quality_report_id=context.quality_report.report_id,
                state=final_state.value,
                config_hash=config_hash
            )
            
            snapshot = ConsolidationLifecycleSnapshot(
                snapshot_id=snapshot_id,
                candidate_id=context.candidate.candidate_id,
                quality_report_id=context.quality_report.report_id,
                parent_candidate_snapshot_version=1, # Stub, from candidate lineage
                quality_report_version=context.quality_report.config_version,
                configuration_version=context.configuration.config_version,
                lifecycle_rule_version=self.rule_version,
                lifecycle_algorithm_version=self.algorithm_version,
                symbol=context.candidate.symbol,
                timeframe=context.candidate.timeframe,
                lifecycle_state=final_state,
                supporting_evidence=evidence_list
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Lifecycle evaluation failure: {str(e)}")
            raise
