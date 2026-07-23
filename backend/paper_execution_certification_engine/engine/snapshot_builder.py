from datetime import datetime, timezone
from backend.paper_execution_certification_engine.models.snapshot import (
    PaperExecutionCertificationSnapshot,
    CertificationReport,
    CertificationMetadata
)
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.config.config import CERTIFICATION_VERSION

class PaperExecutionCertificationSnapshotBuilder:
    """Builds the final immutable certification snapshot."""
    
    @staticmethod
    def build(
        context: PaperExecutionCertificationContext,
        report: CertificationReport,
        execution_duration_ms: float
    ) -> PaperExecutionCertificationSnapshot:
        
        # Generates a deterministic snapshot version
        snapshot_version = f"cert_{report.certification_id}_{report.canonical_hash[:8]}"
        
        metadata = CertificationMetadata(
            certified_at=datetime.now(timezone.utc),
            execution_duration_ms=execution_duration_ms
        )
        
        return PaperExecutionCertificationSnapshot(
            snapshot_version=snapshot_version,
            certification_id=report.certification_id,
            certification_version=CERTIFICATION_VERSION,
            certification_report=report,
            business_fingerprint=report.business_fingerprint,
            canonical_hash=report.canonical_hash,
            parent_execution_snapshot_version=context.optimization_context.execution_context.paper_order_snapshot.snapshot_version,
            certification_metadata=metadata
        )
