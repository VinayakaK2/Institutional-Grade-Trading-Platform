import logging
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import LiquidityGrabLifecycleSnapshot
from backend.liquidity_grab_engine.lifecycle.pipeline.stages import (
    EvidenceGenerationStage,
    LifecycleAggregatorStage,
    SnapshotAssemblyStage
)

logger = logging.getLogger(__name__)

class LiquidityGrabLifecyclePipeline:
    def __init__(
        self,
        evidence_stage: EvidenceGenerationStage,
        aggregator_stage: LifecycleAggregatorStage,
        assembly_stage: SnapshotAssemblyStage
    ) -> None:
        self._evidence_stage = evidence_stage
        self._aggregator_stage = aggregator_stage
        self._assembly_stage = assembly_stage

    def execute(self, context: LiquidityGrabLifecycleContext) -> LiquidityGrabLifecycleSnapshot:
        logger.info(f"Starting Lifecycle Pipeline for Candidate {context.candidate.candidate_id}")
        
        evidence = self._evidence_stage.execute(context)
        summary = self._aggregator_stage.execute(evidence)
        snapshot = self._assembly_stage.execute(context, evidence, summary)
        
        logger.info(f"Lifecycle Pipeline complete. Snapshot ID: {snapshot.snapshot_id}")
        return snapshot
