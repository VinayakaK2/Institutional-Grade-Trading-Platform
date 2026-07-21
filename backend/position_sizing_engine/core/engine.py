import time
from typing import List, cast
from backend.position_sizing_engine.models.context import PositionSizingContext
from backend.position_sizing_engine.models.snapshot import PositionSizingSnapshot, PositionSizingMetadata
from backend.position_sizing_engine.models.report import PositionSizingReport, ValidationResult
from backend.position_sizing_engine.models.evidence import (
    CapitalAllocationEvidence, MaximumRiskEvidence, 
    RawPositionSizeEvidence, RoundLotEvidence, RemainingCashEvidence
)
from backend.position_sizing_engine.validation.contracts import IPositionSizingValidationLayer
from backend.position_sizing_engine.pipeline.pipeline import PositionSizingPipeline
from backend.position_sizing_engine.core.builder import PositionSizingSnapshotBuilder
from backend.position_sizing_engine.contracts.repository import IPositionSizingSnapshotRepository
from backend.position_sizing_engine.exceptions.exceptions import PositionSizingValidationError

class PositionSizingEngine:
    """
    Orchestrates validation, sizing metric pipeline, snapshot building, and persistence.
    Contains no business logic itself.
    """
    def __init__(
        self,
        validation_layers: List[IPositionSizingValidationLayer],
        pipeline: PositionSizingPipeline,
        repository: IPositionSizingSnapshotRepository
    ):
        self._validation_layers = validation_layers
        self._pipeline = pipeline
        self._repository = repository
        
    async def _execute_validation(self, context: PositionSizingContext) -> ValidationResult:
        all_errors = []
        for layer in self._validation_layers:
            res = await layer.validate(context)
            if not res.is_valid:
                all_errors.extend(res.errors)
                if context.configuration.fail_fast:
                    break
        return ValidationResult(is_valid=len(all_errors) == 0, errors=all_errors)
        
    async def execute(self, context: PositionSizingContext) -> PositionSizingSnapshot:
        start_t = time.time()
        
        # 1. Validation
        validation_status = await self._execute_validation(context)
        
        if not validation_status.is_valid and context.configuration.fail_fast:
            raise PositionSizingValidationError(f"Validation failed: {validation_status.errors}")
            
        # 2. Pipeline Execution
        pipeline_results = await self._pipeline.execute(context)
        
        # 3. Assemble Report
        report = PositionSizingReport(
            validation_status=validation_status,
            capital_allocation_evidence=cast(CapitalAllocationEvidence, pipeline_results.get("capital_allocation")) if "capital_allocation" in pipeline_results else None,
            maximum_risk_evidence=cast(MaximumRiskEvidence, pipeline_results.get("maximum_risk")) if "maximum_risk" in pipeline_results else None,
            raw_position_size_evidence=cast(RawPositionSizeEvidence, pipeline_results.get("raw_position_size")) if "raw_position_size" in pipeline_results else None,
            round_lot_evidence=cast(RoundLotEvidence, pipeline_results.get("round_lot_adjustment")) if "round_lot_adjustment" in pipeline_results else None,
            remaining_cash_evidence=cast(RemainingCashEvidence, pipeline_results.get("remaining_cash")) if "remaining_cash" in pipeline_results else None,
            configuration_version=context.configuration.pipeline_version,
            algorithm_version="1.0.0",
            supporting_metadata={}
        )
        
        duration = int((time.time() - start_t) * 1000)
        
        # 4. Collect Metadata
        metadata = PositionSizingMetadata(
            execution_duration_ms=duration,
            additional_info={}
        )
        
        # 5. Build Snapshot
        snapshot = PositionSizingSnapshotBuilder.build(
            context=context,
            report=report,
            metadata=metadata
        )
        
        # 6. Persist
        await self._repository.save(snapshot)
        
        return snapshot
