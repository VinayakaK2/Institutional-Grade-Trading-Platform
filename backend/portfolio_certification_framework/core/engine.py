import logging
from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot
from backend.portfolio_certification_framework.pipeline.stages import (
    FunctionalVerificationStage,
    DeterminismVerificationStage,
    RepositoryVerificationStage,
    StressVerificationStage,
    PerformanceVerificationStage,
    RegressionVerificationStage
)
from backend.portfolio_certification_framework.builders.snapshot_builder import PortfolioCertificationSnapshotBuilder
from backend.portfolio_certification_framework.contracts.repository import IPortfolioCertificationRepository

logger = logging.getLogger(__name__)

class PortfolioCertificationEngine:
    """
    Orchestrates the sequential verification stages to build a certification snapshot.
    """
    def __init__(self, repository: IPortfolioCertificationRepository):
        self._repository = repository
        self._snapshot_builder = PortfolioCertificationSnapshotBuilder()
        
        # Sequential pipeline stages execution order
        self._pipeline_stages = [
            FunctionalVerificationStage(),
            DeterminismVerificationStage(),
            RepositoryVerificationStage(),
            StressVerificationStage(),
            PerformanceVerificationStage(),
            RegressionVerificationStage()
        ]
        
    async def certify(self, execution_context: PortfolioCertificationExecutionContext) -> PortfolioCertificationSnapshot:
        logger.info("[Certification Engine] Starting certification process.")
        
        # Validation checks
        if not execution_context.portfolio_optimization_snapshot:
            raise ValueError("Missing portfolio optimization snapshot for certification.")
            
        # Safe logging via getattr in case of mocked/missing snapshots during edge tests
        snap_id = getattr(execution_context.portfolio_optimization_snapshot, 'snapshot_id', 'MISSING')
        logger.info(f"[Certification Engine] Target Optimization Snapshot: {snap_id}")
        logger.info(f"[Certification Engine] Dataset Version: {execution_context.dataset_version}")
        logger.info(f"[Certification Engine] Configuration Snapshot ID: {execution_context.configuration_snapshot_id}")
        
        # Pipeline execution (Sequential)
        for stage in self._pipeline_stages:
            await stage.execute(execution_context)
            
        # Builder
        snapshot = self._snapshot_builder.build(execution_context)
        
        # Persistence
        await self._repository.save(snapshot)
        
        # Determine overall success
        failed_stages = [s for s in snapshot.certification_report.stages if s.status == "FAIL"]
        if failed_stages:
            logger.error(f"[Certification Engine] Certification FAILED in stages: {[s.stage_name for s in failed_stages]}")
            raise RuntimeError(f"Certification failed for {len(failed_stages)} stages.")
            
        logger.info(f"[Certification Engine] Certification PASSED. Snapshot created: {snapshot.snapshot_id}")
        return snapshot
