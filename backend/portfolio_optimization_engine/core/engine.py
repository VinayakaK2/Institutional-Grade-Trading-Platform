import uuid
import logging
from backend.portfolio_optimization_engine.models.contexts import PortfolioOptimizationExecutionContext, PortfolioOptimizationPipelineContext
from backend.portfolio_optimization_engine.models.snapshot import PortfolioOptimizationSnapshot
from backend.portfolio_optimization_engine.rules.structural_rules import PortfolioOptimizationStructuralRules
from backend.portfolio_optimization_engine.rules.consistency_rules import PortfolioOptimizationConsistencyRules
from backend.portfolio_optimization_engine.builders.snapshot_builder import PortfolioOptimizationSnapshotBuilder
from backend.portfolio_optimization_engine.contracts.repository import IPortfolioOptimizationRepository
from backend.portfolio_optimization_engine.pipeline.optimization_aggregation import PortfolioOptimizationAggregationStage
from backend.portfolio_optimization_engine.pipeline.optimization_metadata import PortfolioOptimizationMetadataStage

logger = logging.getLogger(__name__)

class PortfolioOptimizationEngine:
    """
    Stateless async orchestrator for the Portfolio Optimization Engine.
    Coordinates validation, pipeline execution, building, and repository saving.
    """
    def __init__(self, repository: IPortfolioOptimizationRepository):
        self._repository = repository
        self._structural_rules = PortfolioOptimizationStructuralRules()
        self._consistency_rules = PortfolioOptimizationConsistencyRules()
        self._snapshot_builder = PortfolioOptimizationSnapshotBuilder()
        
        # Pipeline Stages
        self._pipeline_stages = [
            PortfolioOptimizationAggregationStage(),
            PortfolioOptimizationMetadataStage()
        ]
        
    async def optimize(self, execution_context: PortfolioOptimizationExecutionContext) -> PortfolioOptimizationSnapshot:
        execution_id = f"po_exec_{uuid.uuid4()}"
        logger.info(f"[{execution_id}] Starting Portfolio Optimization Engine")
        
        logger.info(f"[{execution_id}] Dataset Version: {execution_context.dataset_version}")
        logger.info(f"[{execution_id}] Configuration Hash: {execution_context.configuration.configuration_hash}")
        logger.info(f"[{execution_id}] Parent State Snapshot: {getattr(execution_context.portfolio_state_snapshot, 'snapshot_id', 'MISSING')}")
        logger.info(f"[{execution_id}] Parent Exposure Snapshot: {getattr(execution_context.portfolio_exposure_snapshot, 'snapshot_id', 'MISSING')}")
        logger.info(f"[{execution_id}] Parent Correlation Snapshot: {getattr(execution_context.portfolio_correlation_snapshot, 'snapshot_id', 'MISSING')}")
        logger.info(f"[{execution_id}] Parent Decision Snapshot: {getattr(execution_context.portfolio_decision_snapshot, 'snapshot_id', 'MISSING')}")
        
        # 1. Validation
        # Will raise exceptions using the Phase 0 exception framework naturally if validation fails
        self._structural_rules.validate(execution_context)
        self._consistency_rules.validate(execution_context)
        
        # 2. Pipeline Execution
        pipeline_context = PortfolioOptimizationPipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )
        
        for stage in self._pipeline_stages:
            pipeline_context = await stage.execute(pipeline_context)
            
        # 3. Snapshot Building
        snapshot = self._snapshot_builder.build(pipeline_context)
        logger.info(f"[{execution_id}] Snapshot built with fingerprint: {snapshot.business_fingerprint}")
        
        # 4. Repository Save
        await self._repository.save(snapshot)
        logger.info(f"[{execution_id}] Snapshot saved to repository: {snapshot.snapshot_id}")
        
        logger.info(f"[{execution_id}] Completed Portfolio Optimization Engine")
        
        return snapshot
