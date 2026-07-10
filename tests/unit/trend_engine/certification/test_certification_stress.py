import pytest
from backend.trend_engine.certification.config.config import CertificationConfig
from backend.trend_engine.certification.dataset.generator import DeterministicDatasetGenerator
from backend.trend_engine.certification.repository.memory import InMemoryCertificationReportRepository
from backend.trend_engine.certification.engine.pipeline import CertificationPipeline
from backend.trend_engine.certification.models.models import VerificationResult

@pytest.mark.asyncio
async def test_certification_stress_repeatability():
    # Only test up to 500 in unit tests to keep tests fast, but we'll do the 3-repeat logic
    config = CertificationConfig(
        enable_stress_testing=True,
        stress_dataset_sizes=[100, 500]
    )
    repo = InMemoryCertificationReportRepository()
    generator = DeterministicDatasetGenerator(seed=42)
    
    pipeline = CertificationPipeline(config=config, repo=repo, generator=generator)
    report = await pipeline.run_certification()
    
    assert report.overall_status == VerificationResult.SUCCESS
    assert report.stage_results["StressVerification"] == VerificationResult.SUCCESS
