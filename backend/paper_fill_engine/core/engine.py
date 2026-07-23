from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot
from backend.paper_fill_engine.contracts.repository import IPaperFillRepository
from backend.paper_fill_engine.validation.structural import StructuralValidator
from backend.paper_fill_engine.validation.consistency import ConsistencyValidator
from backend.paper_fill_engine.core.stages import DeterministicFillStage, LifecycleValidationStage
from backend.paper_fill_engine.builders.snapshot_builder import PaperFillSnapshotBuilder
from backend.paper_fill_engine.logging.logger import PaperFillLogger
from backend.paper_fill_engine.exceptions.exceptions import PaperFillValidationError, PaperFillConsistencyError

class PaperFillEngine:
    """
    Stateless orchestrator for the Fill Simulation Engine.
    """
    def __init__(
        self,
        repository: IPaperFillRepository,
        structural_validator: StructuralValidator,
        consistency_validator: ConsistencyValidator,
        deterministic_fill_stage: DeterministicFillStage,
        lifecycle_validation_stage: LifecycleValidationStage,
        snapshot_builder: PaperFillSnapshotBuilder,
        logger: PaperFillLogger = None
    ):
        self._repository = repository
        self._structural_validator = structural_validator
        self._consistency_validator = consistency_validator
        self._deterministic_fill_stage = deterministic_fill_stage
        self._lifecycle_validation_stage = lifecycle_validation_stage
        self._snapshot_builder = snapshot_builder
        self._logger = logger or PaperFillLogger()

    async def execute(self, context: PaperFillExecutionContext) -> PaperFillSnapshot:
        # 1. Structural Validation
        structural_report = self._structural_validator.validate(context)
        if not structural_report.passed:
            raise PaperFillValidationError(f"Structural validation failed: {structural_report.errors}")
            
        # 2. Consistency Validation
        consistency_report = await self._consistency_validator.validate(context)
        if not consistency_report.passed:
            raise PaperFillConsistencyError(f"Consistency validation failed: {consistency_report.errors}")
            
        # Create Pipeline Context
        pipeline_context = PaperFillPipelineContext(execution_context=context)
        
        # Propagate warnings
        if structural_report.warnings:
            pipeline_context.diagnostics.warnings.extend(structural_report.warnings)
        if consistency_report.warnings:
            pipeline_context.diagnostics.warnings.extend(consistency_report.warnings)
            
        # 3. Deterministic Fill Simulation
        await self._deterministic_fill_stage.execute(context, pipeline_context)
        
        # 4. Lifecycle Validation
        await self._lifecycle_validation_stage.execute(context, pipeline_context)
        
        # 5. Snapshot Builder
        snapshot = self._snapshot_builder.build(context, pipeline_context)
        
        # 6. Repository Save
        self._repository.save(snapshot)
        
        # 7. Log Telemetry
        self._logger.log_pipeline_execution(
            execution_context=context,
            pipeline_context=pipeline_context,
            business_fingerprint=snapshot.business_fingerprint,
            snapshot_version=snapshot.snapshot_version,
            fill_state=snapshot.fill_state.value
        )
        
        # 8. Return Snapshot
        return snapshot
