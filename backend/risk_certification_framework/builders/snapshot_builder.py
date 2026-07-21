from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime, timezone
from backend.risk_certification_framework.models.report import CertificationReport
from backend.risk_certification_framework.models.snapshot import RiskCertificationSnapshot

class RiskCertificationSnapshotBuilder:
    """
    Pure, deterministic builder for RiskCertificationSnapshot.
    """
    def __init__(self):
        self._report: Optional[CertificationReport] = None
        self._certified_phase_version: str = "11.7"
        self._algorithm_version: str = "1.0"
        self._pipeline_version: str = "1.0"
        self._business_fingerprint: Optional[str] = None
        self._metadata: Dict[str, Any] = {}
        
    def with_report(self, report: CertificationReport) -> 'RiskCertificationSnapshotBuilder':
        self._report = report
        return self
        
    def with_business_fingerprint(self, fingerprint: str) -> 'RiskCertificationSnapshotBuilder':
        self._business_fingerprint = fingerprint
        return self
        
    def with_versions(self, phase: str, algorithm: str, pipeline: str) -> 'RiskCertificationSnapshotBuilder':
        self._certified_phase_version = phase
        self._algorithm_version = algorithm
        self._pipeline_version = pipeline
        return self
        
    def with_metadata(self, metadata: Dict[str, Any]) -> 'RiskCertificationSnapshotBuilder':
        self._metadata = metadata
        return self
        
    def build(self) -> RiskCertificationSnapshot:
        if not self._report or not self._business_fingerprint:
            raise ValueError("Report and business fingerprint are required.")
            
        # Generate deterministic snapshot ID based on core attributes
        id_data = {
            "fingerprint": self._business_fingerprint,
            "phase": self._certified_phase_version,
            "algorithm": self._algorithm_version,
            "pipeline": self._pipeline_version
        }
        snapshot_id = "cert_" + hashlib.sha256(json.dumps(id_data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        
        return RiskCertificationSnapshot(
            snapshot_id=snapshot_id,
            report=self._report,
            certified_phase_version=self._certified_phase_version,
            algorithm_version=self._algorithm_version,
            pipeline_version=self._pipeline_version,
            business_fingerprint=self._business_fingerprint,
            metadata=self._metadata,
            generated_timestamp=datetime.now(timezone.utc)
        )
