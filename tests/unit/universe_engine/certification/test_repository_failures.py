import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine
from backend.universe_engine.certification.repository import PostgresCertificationRepository
from backend.universe_engine.certification.models import CertificationReport
from backend.universe_engine.certification.exceptions import CertificationRepositoryError
import uuid
from datetime import datetime, timezone
import pytest_asyncio
from backend.universe_engine.certification.models import UniverseCertificationConfiguration, PerformanceMetrics

@pytest_asyncio.fixture
async def cert_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    # We don't initialize tables to simulate DB errors
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.mark.asyncio
async def test_repository_save_db_error(cert_session_factory):
    repo = PostgresCertificationRepository(cert_session_factory)
    report = CertificationReport(
        certification_id=str(uuid.uuid4()),
        pipeline_version="1.0.0",
        config_hash="abc",
        business_fingerprint_version="1.0.0",
        created_at=datetime.now(timezone.utc),
        configuration_snapshot=UniverseCertificationConfiguration(mode="DETERMINISTIC"),
        functional_passed=True,
        determinism_passed=True,
        integrity_passed=True,
        stress_passed=True,
        is_certified=True,
        test_results={},
        determinism_results={},
        performance_metrics=PerformanceMetrics(execution_time_ms=10.0)
    )
    # Since tables aren't created, this will raise a DB error
    with pytest.raises(CertificationRepositoryError):
        await repo.save_certification_report(report)

@pytest.mark.asyncio
async def test_repository_get_db_error(cert_session_factory):
    repo = PostgresCertificationRepository(cert_session_factory)
    with pytest.raises(CertificationRepositoryError):
        await repo.load_certification_report("any")
