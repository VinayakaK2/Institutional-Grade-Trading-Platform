from backend.portfolio_certification_framework.verification.functional import verify_functional
from backend.portfolio_certification_framework.verification.determinism import verify_determinism
from backend.portfolio_certification_framework.verification.repository import verify_repository
from backend.portfolio_certification_framework.verification.stress import verify_stress
from backend.portfolio_certification_framework.verification.performance import verify_performance
from backend.portfolio_certification_framework.verification.regression import verify_regression
import pytest

@pytest.mark.asyncio
async def test_functional_pass(mock_certification_context):
    result = await verify_functional(mock_certification_context)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_functional_fail(mock_certification_context):
    mock_certification_context.dataset_version = "v2"
    result = await verify_functional(mock_certification_context)
    assert result.status == "FAIL"

@pytest.mark.asyncio
async def test_determinism(mock_certification_context):
    result = await verify_determinism(mock_certification_context)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_repository(mock_certification_context):
    result = await verify_repository(mock_certification_context)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_stress(mock_certification_context):
    result = await verify_stress(mock_certification_context)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_performance(mock_certification_context):
    result = await verify_performance(mock_certification_context)
    assert result.status == "COMPLETED"
    assert "execution_time_ms" in result.metrics
    assert "peak_memory_bytes" in result.metrics

@pytest.mark.asyncio
async def test_regression(mock_certification_context):
    result = await verify_regression(mock_certification_context)
    assert result.status == "FAIL"
    assert "Regression failure: Business Fingerprint changed." in result.error_message
