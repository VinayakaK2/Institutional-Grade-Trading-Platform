import uuid
from backend.portfolio_correlation_engine.models.contexts import PortfolioCorrelationExecutionContext, PortfolioCorrelationPipelineContext
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot
from backend.portfolio_correlation_engine.rules.structural_rules import PortfolioCorrelationStructuralRules
from backend.portfolio_correlation_engine.rules.consistency_rules import PortfolioCorrelationConsistencyRules
from backend.portfolio_correlation_engine.pipeline.pipeline import PortfolioCorrelationPipeline
from backend.portfolio_correlation_engine.builders.snapshot_builder import PortfolioCorrelationSnapshotBuilder
from backend.portfolio_correlation_engine.contracts.repository import IPortfolioCorrelationRepository
from backend.portfolio_correlation_engine.exceptions import PortfolioCorrelationValidationError
from backend.portfolio_correlation_engine.models.references import ParentSnapshotReferences, SnapshotReference

class PortfolioCorrelationEngine:
    """
    Stateless orchestrator for portfolio correlation calculations.
    """
    def __init__(
        self,
        repository: IPortfolioCorrelationRepository,
        structural_rules: PortfolioCorrelationStructuralRules,
        consistency_rules: PortfolioCorrelationConsistencyRules,
        pipeline: PortfolioCorrelationPipeline
    ):
        self._repository = repository
        self._structural_rules = structural_rules
        self._consistency_rules = consistency_rules
        self._pipeline = pipeline
        
    async def execute(self, execution_context: PortfolioCorrelationExecutionContext) -> PortfolioCorrelationSnapshot:
        # 1. Validation
        struct_result = self._structural_rules.validate(execution_context)
        if not struct_result.is_valid:
            raise PortfolioCorrelationValidationError(f"Structural Validation Failed: {struct_result.reason}")
            
        const_result = self._consistency_rules.validate(execution_context)
        if not const_result.is_valid:
            raise PortfolioCorrelationValidationError(f"Consistency Validation Failed: {const_result.reason}")
            
        # 2. Pipeline Execution
        execution_id = str(uuid.uuid4())
        pipeline_context = PortfolioCorrelationPipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )
        
        final_pipeline_context = await self._pipeline.execute(pipeline_context)
        
        # 3. Snapshot Building
        refs = ParentSnapshotReferences(
            portfolio_state_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_state_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_state_snapshot, "pipeline_version", None),
                dataset_version=execution_context.portfolio_state_snapshot.dataset_version
            ),
            portfolio_exposure_snapshot=SnapshotReference(
                snapshot_id=execution_context.portfolio_exposure_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.portfolio_exposure_snapshot, "pipeline_version", None),
                dataset_version=execution_context.portfolio_exposure_snapshot.dataset_version
            ),
            candidate_position_snapshot=SnapshotReference(
                snapshot_id=execution_context.candidate_position_snapshot.snapshot_id,
                snapshot_version=getattr(execution_context.candidate_position_snapshot, "configuration_version", None),
                business_fingerprint=execution_context.candidate_position_snapshot.business_fingerprint,
                dataset_version=execution_context.candidate_position_snapshot.dataset_version
            ),
            risk_decision_snapshot=SnapshotReference(
                snapshot_id=execution_context.risk_decision_snapshot.snapshot_id,
                business_fingerprint=getattr(execution_context.risk_decision_snapshot, "business_fingerprint", None),
                dataset_version=getattr(execution_context.risk_decision_snapshot, "dataset_version", None)
            )
        )
        
        builder = PortfolioCorrelationSnapshotBuilder()
        snapshot = builder \
            .with_correlation_analysis(final_pipeline_context.correlation_analysis) \
            .with_correlation_metrics(final_pipeline_context.correlation_metrics) \
            .with_dataset_version(execution_context.portfolio_state_snapshot.dataset_version) \
            .with_parent_snapshot_references(refs) \
            .with_configuration_snapshot(execution_context.configuration) \
            .with_metadata({
                "execution_id": execution_id,
                "stage_timings": final_pipeline_context.stage_timings
            }) \
            .build()
            
        # 4. Persistence
        await self._repository.save(snapshot)
        
        return snapshot
