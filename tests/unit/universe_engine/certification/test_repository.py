import pytest
import uuid
from datetime import datetime, timezone
from backend.universe_engine.certification.models import CertificationReport, UniverseCertificationConfiguration, PerformanceMetrics
from backend.universe_engine.certification.repository import PostgresCertificationRepository
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.infrastructure.database.orm.base import Base

import pytest_asyncio

@pytest_asyncio.fixture
async def cert_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_save_and_load_certification_report(cert_session_factory):
    repo = PostgresCertificationRepository(cert_session_factory)
    
    report = CertificationReport(
        certification_id=str(uuid.uuid4()),
        pipeline_version="1.0.0",
        config_hash="abc123hash",
        business_fingerprint_version="1.0.0",
        created_at=datetime.now(timezone.utc),
        configuration_snapshot=UniverseCertificationConfiguration(mode="DETERMINISTIC"),
        functional_passed=True,
        determinism_passed=True,
        integrity_passed=True,
        stress_passed=True,
        is_certified=True,
        test_results={"test_metric": True},
        determinism_results={"same_input": True},
        performance_metrics=PerformanceMetrics(execution_time_ms=100.0)
    )
    
    await repo.save_certification_report(report)
    
    loaded = await repo.load_certification_report(report.certification_id)
    
    assert loaded.certification_id == report.certification_id
    assert loaded.is_certified is True
    assert loaded.test_results["test_metric"] is True
    assert loaded.performance_metrics.execution_time_ms == 100.0
