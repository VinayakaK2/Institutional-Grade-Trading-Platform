from backend.risk_certification_framework.models.report import CertificationReport
from backend.risk_certification_framework.models.record import VerificationRecord

from typing import Optional

class CertificationReportBuilder:
    """
    Pure, deterministic builder for the CertificationReport.
    """
    def __init__(self):
        self._functional: Optional[VerificationRecord] = None
        self._determinism: Optional[VerificationRecord] = None
        self._repository: Optional[VerificationRecord] = None
        self._stress: Optional[VerificationRecord] = None
        self._performance: Optional[VerificationRecord] = None
        self._regression: Optional[VerificationRecord] = None
        
    def with_functional(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._functional = record
        return self
        
    def with_determinism(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._determinism = record
        return self
        
    def with_repository(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._repository = record
        return self
        
    def with_stress(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._stress = record
        return self
        
    def with_performance(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._performance = record
        return self
        
    def with_regression(self, record: VerificationRecord) -> 'CertificationReportBuilder':
        self._regression = record
        return self
        
    def build(self) -> CertificationReport:
        records = [
            self._functional, self._determinism, self._repository,
            self._stress, self._performance, self._regression
        ]
        
        if any(r is None for r in records):
            raise ValueError("All certification records must be provided before building.")
            
        overall = "PASS"
        for r in records:
            if r is not None and r.status == "FAIL":
                overall = "FAIL"
                break
                
        # To satisfy MyPy, we assert they are not None after the check above
        assert self._functional is not None
        assert self._determinism is not None
        assert self._repository is not None
        assert self._stress is not None
        assert self._performance is not None
        assert self._regression is not None
                
        return CertificationReport(
            overall_status=overall,
            functional_record=self._functional,
            determinism_record=self._determinism,
            repository_record=self._repository,
            stress_record=self._stress,
            performance_record=self._performance,
            regression_record=self._regression
        )
