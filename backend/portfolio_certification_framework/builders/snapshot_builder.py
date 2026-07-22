import uuid
import hashlib
import json
from datetime import datetime
from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.models.snapshot import PortfolioCertificationSnapshot, PortfolioCertificationMetadata
from backend.portfolio_certification_framework.models.certification_models import CertificationReport

class PortfolioCertificationSnapshotBuilder:
    def build(self, context: PortfolioCertificationExecutionContext) -> PortfolioCertificationSnapshot:
        # Build certification report
        report = CertificationReport(stages=context.stage_results)
        
        # Build payload for hashing
        # Excludes metrics and error_message from business fingerprint to prevent flakiness
        stage_statuses = {stage.stage_name: stage.status for stage in report.stages}
        
        canonical_payload = {
            "portfolio_optimization_snapshot_id": context.portfolio_optimization_snapshot.snapshot_id,
            "dataset_version": context.dataset_version,
            "configuration_snapshot_id": context.configuration_snapshot_id,
            "stage_statuses": stage_statuses
        }
        
        payload_str = json.dumps(canonical_payload, sort_keys=True)
        business_fingerprint = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        metadata = PortfolioCertificationMetadata(
            engine_version="1.0",
            pipeline_version="1.0"
        )
        
        return PortfolioCertificationSnapshot(
            snapshot_id=f"cert_{uuid.uuid4()}",
            schema_version="1.0",
            dataset_version=context.dataset_version,
            created_at=datetime.utcnow(),
            portfolio_optimization_snapshot_id=context.portfolio_optimization_snapshot.snapshot_id,
            configuration_snapshot_id=context.configuration_snapshot_id,
            business_fingerprint=business_fingerprint,
            certification_report=report,
            certification_metadata=metadata
        )
