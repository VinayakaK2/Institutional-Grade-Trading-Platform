import time
from typing import List
from backend.position_risk_engine.models.context import PositionRiskEvaluationContext
from backend.position_risk_engine.models.snapshot import RiskEvaluationSnapshot, PositionRiskMetadata
from backend.position_risk_engine.models.report import RiskEvaluationReport, ValidationResult
from backend.position_risk_engine.validation.contracts import IPositionRiskValidationLayer
from backend.position_risk_engine.pipeline.pipeline import PositionRiskPipeline
from backend.position_risk_engine.core.builder import RiskEvaluationSnapshotBuilder
from backend.position_risk_engine.contracts.repository import IPositionRiskSnapshotRepository
from backend.position_risk_engine.exceptions.exceptions import PositionRiskValidationError

class PositionRiskEvaluationEngine:
    """
    Orchestrates validation, metric pipeline, snapshot building, and persistence.
    Contains no business logic.
    """
    def __init__(
        self,
        validation_layers: List[IPositionRiskValidationLayer],
        pipeline: PositionRiskPipeline,
        repository: IPositionRiskSnapshotRepository
    ):
        self._validation_layers = validation_layers
        self._pipeline = pipeline
        self._repository = repository
        
    async def _execute_validation(self, context: PositionRiskEvaluationContext) -> ValidationResult:
        all_errors = []
        for layer in self._validation_layers:
            res = await layer.validate(context)
            if not res.is_valid:
                all_errors.extend(res.errors)
                if context.configuration.fail_fast:
                    break
        return ValidationResult(is_valid=len(all_errors) == 0, errors=all_errors)
        
    async def execute(self, context: PositionRiskEvaluationContext) -> RiskEvaluationSnapshot:
        start_t = time.time()
        
        # 1. Validation
        validation_status = await self._execute_validation(context)
        
        if not validation_status.is_valid and context.configuration.fail_fast:
            raise PositionRiskValidationError(f"Validation failed: {validation_status.errors}")
            
        # 2. Pipeline Execution
        pipeline_results = await self._pipeline.execute(context)
        
        from typing import cast
        from backend.position_risk_engine.models.evidence import (
            EntryEvidence, StopLossEvidence, DistanceEvidence, 
            AbsoluteRiskEvidence, PercentageRiskEvidence, PerUnitRiskEvidence
        )

        # 3. Assemble Report
        report = RiskEvaluationReport(
            validation_status=validation_status,
            entry_evidence=cast(EntryEvidence, pipeline_results.get("entry_price")) if "entry_price" in pipeline_results else None,
            stop_loss_evidence=cast(StopLossEvidence, pipeline_results.get("stop_loss")) if "stop_loss" in pipeline_results else None,
            distance_evidence=cast(DistanceEvidence, pipeline_results.get("distance")) if "distance" in pipeline_results else None,
            absolute_risk_evidence=cast(AbsoluteRiskEvidence, pipeline_results.get("absolute_risk")) if "absolute_risk" in pipeline_results else None,
            percentage_risk_evidence=cast(PercentageRiskEvidence, pipeline_results.get("percentage_risk")) if "percentage_risk" in pipeline_results else None,
            per_unit_risk_evidence=cast(PerUnitRiskEvidence, pipeline_results.get("per_unit_risk")) if "per_unit_risk" in pipeline_results else None,
            configuration_version=context.configuration.pipeline_version,
            algorithm_version="1.0.0",
            supporting_metadata={}
        )
        
        duration = int((time.time() - start_t) * 1000)
        
        # 4. Collect Metadata
        metadata = PositionRiskMetadata(
            execution_duration_ms=duration,
            additional_info={}
        )
        
        # 5. Build Snapshot
        snapshot = RiskEvaluationSnapshotBuilder.build(
            context=context,
            report=report,
            metadata=metadata
        )
        
        # 6. Persist
        await self._repository.save(snapshot)
        
        return snapshot
