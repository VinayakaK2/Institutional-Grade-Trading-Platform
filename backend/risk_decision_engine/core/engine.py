from typing import List
from typing import cast
import time
import hashlib
import json

from backend.risk_decision_engine.models.context import RiskDecisionContext
from backend.risk_decision_engine.models.snapshot import RiskDecisionSnapshot, RiskDecisionMetadata
from backend.risk_decision_engine.models.report import RiskDecisionReport
from backend.risk_decision_engine.models.evidence import (
    RiskThresholdEvidence, PortfolioDecisionEvidence, ExposureDecisionEvidence,
    SectorDecisionEvidence, CorrelationDecisionEvidence, DailyRiskDecisionEvidence,
    OpenRiskDecisionEvidence
)

from backend.risk_decision_engine.pipeline.pipeline import RiskDecisionPipeline
from backend.risk_decision_engine.pipeline.resolver import DecisionResolver
from backend.risk_decision_engine.pipeline.stages.risk_threshold import RiskThresholdStage
from backend.risk_decision_engine.pipeline.stages.portfolio_constraint import PortfolioConstraintStage
from backend.risk_decision_engine.pipeline.stages.position_exposure import PositionExposureStage
from backend.risk_decision_engine.pipeline.stages.sector_exposure import SectorExposureStage
from backend.risk_decision_engine.pipeline.stages.correlation import CorrelationStage
from backend.risk_decision_engine.pipeline.stages.daily_risk import DailyRiskStage
from backend.risk_decision_engine.pipeline.stages.open_risk import OpenRiskStage

from backend.risk_decision_engine.validation.contracts import IRiskDecisionValidationLayer
from backend.risk_decision_engine.exceptions.exceptions import RiskDecisionValidationError, RiskDecisionBuilderError
from backend.risk_decision_engine.core.builder import RiskDecisionSnapshotBuilder
from backend.risk_decision_engine.contracts.repository import IRiskDecisionSnapshotRepository

class RiskDecisionEngine:
    """
    Orchestrates the entire Risk Decision process.
    Contains zero business logic.
    """
    def __init__(
        self,
        validation_layers: List[IRiskDecisionValidationLayer],
        repository: IRiskDecisionSnapshotRepository,
        algorithm_version: str = "1.0.0"
    ):
        self._validation_layers = validation_layers
        self._repository = repository
        self._algorithm_version = algorithm_version
        
        # Instantiate stages
        self._pipeline = RiskDecisionPipeline([
            RiskThresholdStage(),
            PortfolioConstraintStage(),
            PositionExposureStage(),
            SectorExposureStage(),
            CorrelationStage(),
            DailyRiskStage(),
            OpenRiskStage()
        ])
        
        self._resolver = DecisionResolver()
        
    async def evaluate(self, context: RiskDecisionContext) -> RiskDecisionSnapshot:
        start_time = time.perf_counter()
        
        # 1. Validation
        if context.configuration.validation_enabled:
            for layer in self._validation_layers:
                result = await layer.validate(context)
                if not result.is_valid:
                    raise RiskDecisionValidationError(f"Validation failed: {', '.join(result.errors)}")
        
        # 2. Pipeline Execution
        evidence_map = await self._pipeline.run(context)
        
        # Calculate a deterministic precursor ID to pass to the resolver
        # This isn't the final snapshot_id but acts as a unique seed for metric IDs
        precursor_hash = hashlib.sha256(
            json.dumps({"risk": context.parent_snapshots.risk_snapshot_id, "sizing": context.parent_snapshots.sizing_snapshot_id}, sort_keys=True).encode()
        ).hexdigest()
        
        # 3. Decision Resolution
        final_evidence = self._resolver.resolve(
            evidence_map=evidence_map,
            snapshot_id=precursor_hash,
            algorithm_version=self._algorithm_version
        )
        
        # 4. Report Assembly
        report = RiskDecisionReport(
            validation_status=result if context.configuration.validation_enabled else None, # type: ignore
            risk_threshold_evidence=cast(RiskThresholdEvidence, evidence_map[RiskThresholdStage]),
            portfolio_constraint_evidence=cast(PortfolioDecisionEvidence, evidence_map[PortfolioConstraintStage]),
            position_exposure_evidence=cast(ExposureDecisionEvidence, evidence_map[PositionExposureStage]),
            sector_exposure_evidence=cast(SectorDecisionEvidence, evidence_map[SectorExposureStage]),
            correlation_evidence=cast(CorrelationDecisionEvidence, evidence_map[CorrelationStage]),
            daily_risk_evidence=cast(DailyRiskDecisionEvidence, evidence_map[DailyRiskStage]),
            open_risk_evidence=cast(OpenRiskDecisionEvidence, evidence_map[OpenRiskStage]),
            final_decision_evidence=final_evidence,
            configuration_version=context.configuration.pipeline_version,
            algorithm_version=self._algorithm_version
        )
        
        # 5. Build Snapshot
        try:
            snapshot_id = RiskDecisionSnapshotBuilder.generate_snapshot_id(
                context=context,
                algorithm_version=self._algorithm_version,
                decision=final_evidence.decision
            )
        except Exception as e:
            raise RiskDecisionBuilderError(f"Failed to build snapshot: {str(e)}")
            
        execution_duration = (time.perf_counter() - start_time) * 1000
        metadata = RiskDecisionMetadata(
            execution_duration_ms=execution_duration,
            additional_info={}
        )
        
        snapshot = RiskDecisionSnapshot(
            snapshot_id=snapshot_id,
            context=context,
            report=report,
            metadata=metadata
        )
        
        # 6. Persist
        await self._repository.save(snapshot)
        
        return snapshot
