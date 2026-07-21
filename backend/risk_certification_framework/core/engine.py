from typing import Any, Dict
from backend.risk_certification_framework.builders.report_builder import CertificationReportBuilder
from backend.risk_certification_framework.builders.snapshot_builder import RiskCertificationSnapshotBuilder
from backend.risk_certification_framework.contracts.repository import IRiskCertificationRepository
from backend.risk_certification_framework.certifiers.functional import FunctionalCertifier
from backend.risk_certification_framework.certifiers.determinism import DeterminismCertifier
from backend.risk_certification_framework.certifiers.repository import RepositoryCertifier
from backend.risk_certification_framework.certifiers.stress import StressCertifier
from backend.risk_certification_framework.certifiers.performance import PerformanceCertifier
from backend.risk_certification_framework.certifiers.regression import RegressionCertifier
from backend.risk_certification_framework.models.snapshot import RiskCertificationSnapshot

class CertificationEngine:
    """
    Thin orchestrator for the certification pipeline.
    Contains no business logic. Routes requests sequentially through certifiers.
    """
    def __init__(
        self,
        repository: IRiskCertificationRepository,
        functional_certifier: FunctionalCertifier,
        determinism_certifier: DeterminismCertifier,
        repository_certifier: RepositoryCertifier,
        stress_certifier: StressCertifier,
        performance_certifier: PerformanceCertifier,
        regression_certifier: RegressionCertifier
    ):
        self._repository = repository
        self._functional_certifier = functional_certifier
        self._determinism_certifier = determinism_certifier
        self._repository_certifier = repository_certifier
        self._stress_certifier = stress_certifier
        self._performance_certifier = performance_certifier
        self._regression_certifier = regression_certifier
        
    async def execute_certification(
        self,
        snapshot: Any,
        seq_output: Any,
        par_output: Any,
        stress_result: Any,
        perf_metrics: Dict[str, Any],
        phase_11_5_output: Any,
        phase_11_6_output: Any,
        business_fingerprint: str
    ) -> RiskCertificationSnapshot:
        
        # 1. Functional
        func_rec = await self._functional_certifier.verify(snapshot)
        
        # 2. Determinism
        det_rec = await self._determinism_certifier.verify(seq_output, par_output)
        
        # 3. Repository
        # We need a dummy snapshot to test repo invariants
        builder = RiskCertificationSnapshotBuilder()
        builder.with_business_fingerprint("dummy_hash")
        # For the test, we mock a valid enough snapshot structure. The repository certifier will handle it.
        # Actually, let's just pass a generic mocked snapshot to the repository certifier
        repo_rec = await self._repository_certifier.verify(self._repository, snapshot)
        
        # 4. Stress
        stress_rec = await self._stress_certifier.verify(stress_result)
        
        # 5. Performance
        perf_rec = await self._performance_certifier.verify(perf_metrics)
        
        # 6. Regression
        reg_rec = await self._regression_certifier.verify(phase_11_5_output, phase_11_6_output)
        
        # 7. Build Report
        report_builder = CertificationReportBuilder()
        report = report_builder \
            .with_functional(func_rec) \
            .with_determinism(det_rec) \
            .with_repository(repo_rec) \
            .with_stress(stress_rec) \
            .with_performance(perf_rec) \
            .with_regression(reg_rec) \
            .build()
            
        # 8. Build Snapshot
        snapshot_builder = RiskCertificationSnapshotBuilder()
        final_snapshot = snapshot_builder \
            .with_report(report) \
            .with_business_fingerprint(business_fingerprint) \
            .with_versions(phase="11.7", algorithm="1.0", pipeline="1.0") \
            .build()
            
        # 9. Persist
        await self._repository.insert(final_snapshot)
        
        return final_snapshot
