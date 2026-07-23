import time
import uuid
from backend.paper_execution_certification_engine.models.snapshot import PaperExecutionCertificationSnapshot
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.engine.pipeline import PaperExecutionCertificationPipeline
from backend.paper_execution_certification_engine.engine.report_builder import PaperExecutionCertificationReportBuilder
from backend.paper_execution_certification_engine.engine.snapshot_builder import PaperExecutionCertificationSnapshotBuilder
from backend.paper_execution_certification_engine.contracts.repository import IPaperExecutionCertificationRepository
from backend.paper_execution_certification_engine.exceptions.exceptions import CertificationFailedError

class PaperExecutionCertificationEngine:
    """
    Independent verification engine. 
    Never becomes part of the production execution path.
    """
    
    def __init__(self, repository: IPaperExecutionCertificationRepository):
        self._repository = repository
        self._pipeline = PaperExecutionCertificationPipeline()
        
    async def certify(self, context: PaperExecutionCertificationContext) -> PaperExecutionCertificationSnapshot:
        """
        Executes the certification pipeline and persists the resulting snapshot.
        If certification fails and config dictates fail_fast, an exception is raised 
        during the pipeline. Otherwise, it still builds a report with failure state, 
        but we generally enforce 'never silently continue after certification failures'.
        """
        start_time = time.time()
        
        # 1. Execute Pipeline Stages sequentially
        stage_results = await self._pipeline.execute(context)
        
        # 2. Assert no failures (never silently continue)
        for result in stage_results:
            if not result.passed:
                raise CertificationFailedError(f"Certification failed at stage: {result.stage_name}. Error: {result.error_message}")
        
        # 3. Build Certification Report
        # Generate a unique Certification ID for this run
        certification_id = f"CERT-{time.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        report = PaperExecutionCertificationReportBuilder.build(
            context=context,
            stage_results=stage_results,
            certification_id=certification_id
        )
        
        # 4. Build Immutable Snapshot
        execution_duration_ms = (time.time() - start_time) * 1000
        snapshot = PaperExecutionCertificationSnapshotBuilder.build(
            context=context,
            report=report,
            execution_duration_ms=execution_duration_ms
        )
        
        # 5. Persist to Append-Only Repository
        await self._repository.save(snapshot)
        
        return snapshot
