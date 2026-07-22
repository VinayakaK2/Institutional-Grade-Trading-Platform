from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot
from backend.paper_order_engine.contracts.repository import IPaperOrderRepository
from backend.paper_order_engine.core.pipeline import PipelineExecutor
from backend.paper_order_engine.validation.structural import StructuralValidator
from backend.paper_order_engine.validation.consistency import ConsistencyValidator
from backend.paper_order_engine.builders.snapshot_builder import PaperOrderSnapshotBuilder
from backend.paper_order_engine.logging.logger import PaperOrderLogger
from backend.paper_order_engine.exceptions.exceptions import PaperOrderValidationError, PaperOrderConsistencyError

class PaperOrderEngine:
    """
    Stateless orchestrator for the Order Simulation Engine.
    """
    def __init__(
        self,
        repository: IPaperOrderRepository,
        structural_validator: StructuralValidator,
        consistency_validator: ConsistencyValidator,
        pipeline_executor: PipelineExecutor,
        snapshot_builder: PaperOrderSnapshotBuilder,
        logger: PaperOrderLogger = None
    ):
        self._repository = repository
        self._structural_validator = structural_validator
        self._consistency_validator = consistency_validator
        self._pipeline_executor = pipeline_executor
        self._snapshot_builder = snapshot_builder
        self._logger = logger or PaperOrderLogger()

    async def execute(self, context: PaperOrderExecutionContext) -> PaperOrderSnapshot:
        # 1. Structural Validation
        structural_report = self._structural_validator.validate(context)
        if not structural_report.passed:
            raise PaperOrderValidationError(f"Structural validation failed: {structural_report.errors}")
            
        # 2. Consistency Validation
        consistency_report = await self._consistency_validator.validate(context)
        if not consistency_report.passed:
            raise PaperOrderConsistencyError(f"Consistency validation failed: {consistency_report.errors}")
            
        # 3. Create Pipeline Context
        pipeline_context = PaperOrderPipelineContext(execution_context=context)
        
        # Propagate warnings
        if structural_report.warnings:
            pipeline_context.diagnostics.structural_validation_warnings = structural_report.warnings
        if consistency_report.warnings:
            pipeline_context.diagnostics.consistency_validation_warnings = consistency_report.warnings
            
        # 4. Execute Pipeline
        await self._pipeline_executor.execute(context, pipeline_context)
        
        # 5. Build Snapshot
        snapshot = self._snapshot_builder.build(context, pipeline_context)
        
        # 6. Persist
        self._repository.save(snapshot)
        
        # 7. Log Telemetry
        self._logger.log_pipeline_execution(
            execution_context=context,
            pipeline_context=pipeline_context,
            business_fingerprint=snapshot.business_fingerprint,
            snapshot_version=snapshot.snapshot_version
        )
        
        return snapshot
