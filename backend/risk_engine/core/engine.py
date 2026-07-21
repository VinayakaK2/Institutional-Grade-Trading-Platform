import time
from typing import List
from backend.risk_engine.models.context import RiskExecutionContext
from backend.risk_engine.models.snapshot import RiskSnapshot, ValidationResult, RiskMetadata
from backend.risk_engine.validation.contracts import IValidationLayer
from backend.risk_engine.pipeline.pipeline import RiskPipeline
from backend.risk_engine.core.builder import RiskSnapshotBuilder
from backend.risk_engine.contracts.repository import IRiskSnapshotRepository
from backend.risk_engine.exceptions.exceptions import RiskValidationError

class RiskEngine:
    """
    Core Risk Engine Orchestrator.
    Executes validation, pipeline, builds snapshot, and persists.
    Contains absolutely zero business logic.
    """
    def __init__(
        self,
        validation_layers: List[IValidationLayer],
        pipeline: RiskPipeline,
        repository: IRiskSnapshotRepository
    ):
        self._validation_layers = validation_layers
        self._pipeline = pipeline
        self._repository = repository
        
    async def _execute_validation(self, context: RiskExecutionContext) -> ValidationResult:
        all_errors = []
        for layer in self._validation_layers:
            res = await layer.validate(context)
            if not res.is_valid:
                all_errors.extend(res.errors)
                if context.configuration.fail_fast:
                    break
                    
        return ValidationResult(is_valid=len(all_errors) == 0, errors=all_errors)
        
    async def execute(self, context: RiskExecutionContext) -> RiskSnapshot:
        start_t = time.time()
        
        # 1. Validation
        validation_status = await self._execute_validation(context)
        
        if not validation_status.is_valid and context.configuration.fail_fast:
            raise RiskValidationError(f"Validation failed: {validation_status.errors}")
            
        # 2. Pipeline Execution
        pipeline_result = await self._pipeline.execute(context)
        
        duration = int((time.time() - start_t) * 1000)
        
        # 3. Metadata Collection
        metadata = RiskMetadata(
            pipeline_version=context.configuration.pipeline_version,
            execution_duration_ms=duration,
            additional_info={}
        )
        
        # 4. Build Snapshot
        snapshot = RiskSnapshotBuilder.build(
            context=context,
            pipeline_result=pipeline_result,
            validation_status=validation_status,
            metadata=metadata
        )
        
        # 5. Persist Snapshot
        await self._repository.save(snapshot)
        
        return snapshot
