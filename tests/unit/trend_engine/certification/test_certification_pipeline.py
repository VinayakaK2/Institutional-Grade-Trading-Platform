import pytest
from backend.trend_engine.certification.config.config import CertificationConfig
from backend.trend_engine.certification.dataset.generator import DeterministicDatasetGenerator
from backend.trend_engine.certification.repository.memory import InMemoryCertificationReportRepository
from backend.trend_engine.certification.engine.pipeline import CertificationPipeline
from backend.trend_engine.certification.models.models import VerificationResult

@pytest.mark.asyncio
async def test_certification_pipeline_success():
    config = CertificationConfig(enable_stress_testing=False, enable_determinism_checks=True)
    repo = InMemoryCertificationReportRepository()
    generator = DeterministicDatasetGenerator(seed=42)
    
    pipeline = CertificationPipeline(config=config, repo=repo, generator=generator)
    report = await pipeline.run_certification()
    
    assert report.overall_status == VerificationResult.SUCCESS
    assert report.stage_results["FunctionalVerification"] == VerificationResult.SUCCESS
    assert report.stage_results["DeterminismVerification"] == VerificationResult.SUCCESS
    assert report.stage_results["RepositoryVerification"] == VerificationResult.SUCCESS
    assert report.stage_results["StressVerification"] == VerificationResult.SUCCESS # skipped/passed
    assert report.stage_results["PerformanceVerification"] == VerificationResult.SKIPPED
    assert report.stage_results["CertificationSummary"] == VerificationResult.SUCCESS
    
    assert report.metrics.dataset_size == 100
    
    # Verify repository saved
    latest = await repo.load_latest()
    assert latest is not None
    assert latest.overall_status == VerificationResult.SUCCESS
