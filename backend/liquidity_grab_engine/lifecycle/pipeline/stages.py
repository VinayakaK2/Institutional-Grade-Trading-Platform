import logging
import datetime
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import (
    LifecycleEvidence,
    LifecycleSummary,
    LiquidityGrabLifecycleSnapshot
)
from backend.liquidity_grab_engine.lifecycle.registry.registry import EvidenceRegistry
from backend.liquidity_grab_engine.lifecycle.contracts.aggregator import ILifecycleAggregator

logger = logging.getLogger(__name__)

class EvidenceGenerationStage:
    def __init__(self, registry: EvidenceRegistry) -> None:
        self._registry = registry

    def execute(self, context: LiquidityGrabLifecycleContext) -> LifecycleEvidence:
        logger.info("Executing EvidenceGenerationStage")
        return self._registry.execute(context)

class LifecycleAggregatorStage:
    def __init__(self, aggregator: ILifecycleAggregator) -> None:
        self._aggregator = aggregator

    def execute(self, evidence: LifecycleEvidence) -> LifecycleSummary:
        logger.info("Executing LifecycleAggregatorStage")
        return self._aggregator.aggregate(evidence)

class SnapshotAssemblyStage:
    """
    Constructs the immutable LiquidityGrabLifecycleSnapshot.
    Rule: Must remain logic-free. It must ONLY collect outputs, construct the immutable snapshot,
    assign metadata, and calculate deterministic snapshot ID. It must NEVER evaluate evidence,
    modify state, or change confidence. All lifecycle decisions belong exclusively inside LifecycleAggregator.
    """
    def execute(self, context: LiquidityGrabLifecycleContext, evidence: LifecycleEvidence, summary: LifecycleSummary) -> LiquidityGrabLifecycleSnapshot:
        logger.info("Executing SnapshotAssemblyStage")
        
        config_hash = context.configuration.generate_hash()
        
        snapshot_id = LiquidityGrabLifecycleSnapshot.generate_id(
            candidate_id=context.candidate.candidate_id,
            dataset_version=context.dataset_version,
            config_hash=config_hash,
            aggregator_version=summary.aggregator_version
        )
        
        metadata = {
            "pipeline_version": context.metadata.pipeline_version,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "quality_report_id": context.quality_report.report_id
        }
        
        return LiquidityGrabLifecycleSnapshot(
            snapshot_id=snapshot_id,
            candidate_id=context.candidate.candidate_id,
            symbol_id=context.candidate.symbol_id,
            timeframe=context.candidate.timeframe,
            evidence=evidence,
            summary=summary,
            metadata=metadata
        )
