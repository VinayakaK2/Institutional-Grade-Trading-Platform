import pytest
from backend.risk_certification_framework.core.engine import CertificationEngine
from backend.risk_certification_framework.repository.memory import MemoryCertificationRepository
from backend.risk_certification_framework.certifiers.functional import FunctionalCertifier
from backend.risk_certification_framework.certifiers.determinism import DeterminismCertifier
from backend.risk_certification_framework.certifiers.repository import RepositoryCertifier
from backend.risk_certification_framework.certifiers.stress import StressCertifier
from backend.risk_certification_framework.certifiers.performance import PerformanceCertifier
from backend.risk_certification_framework.certifiers.regression import RegressionCertifier
from backend.risk_certification_framework.builders.snapshot_builder import RiskCertificationSnapshotBuilder
from backend.risk_certification_framework.models.report import CertificationReport
from backend.risk_certification_framework.models.record import VerificationRecord

class MockSnapshot:
    def __init__(self, id_val: str):
        self.snapshot_id = id_val
        self.report = "mock"

def build_mock_snapshot(id_val: str):
    builder = RiskCertificationSnapshotBuilder()
    report = CertificationReport(
        overall_status="PASS",
        functional_record=VerificationRecord(certifier_name="F", status="PASS", evidence=""),
        determinism_record=VerificationRecord(certifier_name="D", status="PASS", evidence=""),
        repository_record=VerificationRecord(certifier_name="R", status="PASS", evidence=""),
        stress_record=VerificationRecord(certifier_name="S", status="PASS", evidence=""),
        performance_record=VerificationRecord(certifier_name="P", status="PASS", evidence=""),
        regression_record=VerificationRecord(certifier_name="Reg", status="PASS", evidence="")
    )
    return builder.with_business_fingerprint("fphash").with_report(report).build()

@pytest.mark.asyncio
async def test_full_certification_pipeline():
    repo = MemoryCertificationRepository()
    engine = CertificationEngine(
        repository=repo,
        functional_certifier=FunctionalCertifier(),
        determinism_certifier=DeterminismCertifier(),
        repository_certifier=RepositoryCertifier(),
        stress_certifier=StressCertifier(),
        performance_certifier=PerformanceCertifier(),
        regression_certifier=RegressionCertifier()
    )
    
    mock_snapshot = build_mock_snapshot("123")
    
    final_snapshot = await engine.execute_certification(
        snapshot=mock_snapshot,
        seq_output="identical_output",
        par_output="identical_output",
        stress_result="success",
        perf_metrics={"cpu": "10ms"},
        phase_11_5_output="identical_decision",
        phase_11_6_output="identical_decision",
        business_fingerprint="some_fp"
    )
    
    assert final_snapshot.report.overall_status == "PASS"
    assert final_snapshot.report.functional_record.status == "PASS"
    assert final_snapshot.report.determinism_record.status == "PASS"
    assert final_snapshot.report.repository_record.status == "PASS"
    assert final_snapshot.report.stress_record.status == "PASS"
    assert final_snapshot.report.performance_record.status == "PASS"
    assert final_snapshot.report.regression_record.status == "PASS"
    
    # Assert repository preserved it
    persisted = await repo.get(final_snapshot.snapshot_id)
    assert persisted.snapshot_id == final_snapshot.snapshot_id

@pytest.mark.asyncio
async def test_determinism_failure():
    repo = MemoryCertificationRepository()
    engine = CertificationEngine(
        repository=repo,
        functional_certifier=FunctionalCertifier(),
        determinism_certifier=DeterminismCertifier(),
        repository_certifier=RepositoryCertifier(),
        stress_certifier=StressCertifier(),
        performance_certifier=PerformanceCertifier(),
        regression_certifier=RegressionCertifier()
    )
    
    mock_snapshot = build_mock_snapshot("123")
    
    final_snapshot = await engine.execute_certification(
        snapshot=mock_snapshot,
        seq_output="identical_output",
        par_output="DIFFERENT_OUTPUT",
        stress_result="success",
        perf_metrics={"cpu": "10ms"},
        phase_11_5_output="identical_decision",
        phase_11_6_output="identical_decision",
        business_fingerprint="some_fp"
    )
    
    assert final_snapshot.report.overall_status == "FAIL"
    assert final_snapshot.report.determinism_record.status == "FAIL"

@pytest.mark.asyncio
async def test_regression_failure():
    repo = MemoryCertificationRepository()
    engine = CertificationEngine(
        repository=repo,
        functional_certifier=FunctionalCertifier(),
        determinism_certifier=DeterminismCertifier(),
        repository_certifier=RepositoryCertifier(),
        stress_certifier=StressCertifier(),
        performance_certifier=PerformanceCertifier(),
        regression_certifier=RegressionCertifier()
    )
    
    mock_snapshot = build_mock_snapshot("123")
    
    final_snapshot = await engine.execute_certification(
        snapshot=mock_snapshot,
        seq_output="identical_output",
        par_output="identical_output",
        stress_result="success",
        perf_metrics={"cpu": "10ms"},
        phase_11_5_output="identical_decision",
        phase_11_6_output="DIFFERENT_DECISION",
        business_fingerprint="some_fp"
    )
    
    assert final_snapshot.report.overall_status == "FAIL"
    assert final_snapshot.report.regression_record.status == "FAIL"
