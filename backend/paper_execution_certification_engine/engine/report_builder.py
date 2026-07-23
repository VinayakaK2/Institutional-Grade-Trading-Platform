from datetime import datetime, timezone
from typing import List
import hashlib
from backend.paper_execution_certification_engine.models.snapshot import (
    CertificationReport,
    StageResult
)
from backend.paper_execution_certification_engine.models.contexts import PaperExecutionCertificationContext
from backend.paper_execution_certification_engine.config.config import CERTIFICATION_VERSION

class PaperExecutionCertificationReportBuilder:
    """Builds the rich summary report for the certification snapshot."""
    
    @staticmethod
    def build(
        context: PaperExecutionCertificationContext,
        stage_results: List[StageResult],
        certification_id: str
    ) -> CertificationReport:
        
        all_passed = all(stage.passed for stage in stage_results)
        
        # We need a stable canonical hash.
        # It explicitly EXCLUDES volatile fields such as timestamps, execution IDs, 
        # and runtime performance metrics to guarantee determinism.
        hash_payload = (
            f"{context.optimization_context.execution_context.configuration_hash}_"
            f"{context.synthetic_dataset_a_hash}_{context.synthetic_dataset_b_hash}_"
            f"{context.replay_dataset_hash}_{context.stress_dataset_hash}"
        )
        canonical_hash = hashlib.sha256(hash_payload.encode()).hexdigest()
        
        evidence_count = sum(len(stage.evidence) for stage in stage_results)
        
        # Get the actual engine version logic ideally, but mocking for isolated cert engine
        return CertificationReport(
            certification_id=certification_id,
            certification_schema_version="1.0.0",
            certified=all_passed,
            paper_execution_version="1.0.0",
            optimization_version="1.0.0",
            certification_version=CERTIFICATION_VERSION,
            timestamp=datetime.now(timezone.utc).isoformat(),
            business_fingerprint=context.optimization_context.execution_context.paper_order_snapshot.business_fingerprint,
            canonical_hash=canonical_hash,
            evidence_count=evidence_count,
            verified_stages=stage_results
        )
