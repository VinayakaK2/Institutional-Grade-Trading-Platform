import logging
from backend.paper_execution_engine.models.contexts import PaperExecutionContext, PaperExecutionPipelineContext
from backend.paper_execution_engine.models.snapshot import PaperExecutionSnapshot
from backend.paper_execution_engine.contracts.repository import IPaperExecutionRepository
from backend.paper_execution_engine.validation.structural import StructuralValidator
from backend.paper_execution_engine.validation.consistency import ConsistencyValidator
from backend.paper_execution_engine.core.pipeline import PipelineExecutor
from backend.paper_execution_engine.builders.snapshot_builder import PaperExecutionSnapshotBuilder

logger = logging.getLogger(__name__)

class PaperExecutionEngine:
    """
    Thin orchestrator for the Paper Execution framework.
    Completely stateless: No caching, no mutable members, no singleton state.
    Every execution is independent.
    """
    
    def __init__(
        self,
        repository: IPaperExecutionRepository,
        structural_validator: StructuralValidator,
        consistency_validator: ConsistencyValidator,
        pipeline_executor: PipelineExecutor,
        snapshot_builder: PaperExecutionSnapshotBuilder
    ):
        self._repository = repository
        self._structural_validator = structural_validator
        self._consistency_validator = consistency_validator
        self._pipeline_executor = pipeline_executor
        self._snapshot_builder = snapshot_builder
        
    async def execute(self, context: PaperExecutionContext) -> PaperExecutionSnapshot:
        """
        Orchestrates the execution lifecycle safely.
        """
        # 1. Structural Validation
        structural_report = self._structural_validator.validate(context)
        if not structural_report.passed:
            logger.error(f"Structural validation failed: {structural_report.errors}")
            raise ValueError(f"Structural validation failed: {structural_report.errors}")
            
        # 2. Consistency Validation
        consistency_report = await self._consistency_validator.validate(context)
        if not consistency_report.passed:
            logger.error(f"Consistency validation failed: {consistency_report.errors}")
            raise ValueError(f"Consistency validation failed: {consistency_report.errors}")
            
        # 3. Create Pipeline Context
        pipeline_context = PaperExecutionPipelineContext()
        
        # Propagate validation warnings to diagnostics
        if structural_report.warnings:
            pipeline_context.diagnostics["structural_validation_warnings"] = structural_report.warnings
        if consistency_report.warnings:
            pipeline_context.diagnostics["consistency_validation_warnings"] = consistency_report.warnings
        
        # 4. Execute Pipeline
        await self._pipeline_executor.execute(context, pipeline_context)
        
        # 5. Build Snapshot
        snapshot = self._snapshot_builder.build(context, pipeline_context)
        
        # 6. Persist Snapshot
        await self._repository.save(snapshot)
        
        # Structural logging per requirements
        logger.info(
            "Paper execution completed successfully",
            extra={
                "pipeline_version": context.configuration.pipeline_version,
                "configuration_hash": snapshot.configuration_hash,
                "dataset_version": context.dataset_version,
                "parent_portfolio_decision_snapshot_version": context.parent_portfolio_decision_snapshot_version,
                "snapshot_version": snapshot.snapshot_version,
                "business_fingerprint": snapshot.business_fingerprint
            }
        )
        
        return snapshot
