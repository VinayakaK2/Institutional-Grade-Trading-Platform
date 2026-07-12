from abc import ABC, abstractmethod
from typing import Optional
from backend.liquidity_grab_engine.detection.models.context import LiquidityGrabDetectionContext
from backend.liquidity_grab_engine.detection.models.models import DetectionEvidence, LiquidityGrabCandidate, CandidateMetadata
from backend.liquidity_grab_engine.detection.contracts.strategies import (
    ISupportBreakDetectionStrategy,
    IRecoveryDetectionStrategy,
    IFalseBreakValidationStrategy
)

class ILiquidityGrabDetectionStage(ABC):
    """
    Interface for a detection pipeline stage.
    """
    @abstractmethod
    def execute(self, context: LiquidityGrabDetectionContext, evidence: DetectionEvidence) -> DetectionEvidence:
        pass

class SupportBreakDetectionStage(ILiquidityGrabDetectionStage):
    def __init__(self, strategy: ISupportBreakDetectionStrategy):
        self.strategy = strategy

    def execute(self, context: LiquidityGrabDetectionContext, evidence: DetectionEvidence) -> DetectionEvidence:
        detected = self.strategy.detect(context)
        return evidence.model_copy(update={"support_break_detected": detected})

class RecoveryDetectionStage(ILiquidityGrabDetectionStage):
    def __init__(self, strategy: IRecoveryDetectionStrategy):
        self.strategy = strategy

    def execute(self, context: LiquidityGrabDetectionContext, evidence: DetectionEvidence) -> DetectionEvidence:
        detected = self.strategy.detect(context)
        return evidence.model_copy(update={"recovery_detected": detected})

class FalseBreakValidationStage(ILiquidityGrabDetectionStage):
    def __init__(self, strategy: IFalseBreakValidationStrategy):
        self.strategy = strategy

    def execute(self, context: LiquidityGrabDetectionContext, evidence: DetectionEvidence) -> DetectionEvidence:
        validated = self.strategy.validate(context)
        return evidence.model_copy(update={"false_break_validated": validated})

class CandidateAssemblyStage:
    """
    Dedicated stage for constructing the immutable LiquidityGrabCandidate.
    No business logic happens here. Just candidate assembly from context and evidence.
    """
    def execute(self, context: LiquidityGrabDetectionContext, evidence: DetectionEvidence, strategy_versions: dict = None) -> Optional[LiquidityGrabCandidate]:
        if not (evidence.support_break_detected and evidence.recovery_detected and evidence.false_break_validated):
            return None # Candidate not fully formed
            
        strategy_versions = strategy_versions or {}
        
        candidate_id = LiquidityGrabCandidate.generate_id(
            symbol_id=context.market_data.symbol.symbol,
            dataset_version=context.dataset.version,
            trend_version=context.parent_snapshots.trend_snapshot_version,
            consolidation_version=context.parent_snapshots.consolidation_snapshot_version,
            config_hash=context.configuration.generate_hash()
        )
        
        return LiquidityGrabCandidate(
            candidate_id=candidate_id,
            symbol_id=context.market_data.symbol.symbol,
            timeframe=context.market_data.timeframe.value,
            dataset_version=context.dataset.version,
            parent_trend_snapshot_version=context.parent_snapshots.trend_snapshot_version,
            parent_consolidation_snapshot_version=context.parent_snapshots.consolidation_snapshot_version,
            configuration_hash=context.configuration.generate_hash(),
            evidence=evidence,
            metadata=CandidateMetadata(
                pipeline_version=context.metadata.pipeline_version,
                strategy_versions=strategy_versions
            )
        )
