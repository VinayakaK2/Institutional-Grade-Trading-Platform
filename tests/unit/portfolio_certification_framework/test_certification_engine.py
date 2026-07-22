import pytest
from backend.portfolio_certification_framework.core.engine import PortfolioCertificationEngine
from backend.portfolio_certification_framework.repository.memory_repo import MemoryPortfolioCertificationRepository

@pytest.mark.asyncio
async def test_certification_engine_failure(mock_certification_context):
    repo = MemoryPortfolioCertificationRepository()
    engine = PortfolioCertificationEngine(repository=repo)
    
    # The regression verification stage will fail because the mock context
    # provides an invalid synthetic business_fingerprint ("opt_fp_1").
    # The engine correctly captures this and raises RuntimeError at the end.
    with pytest.raises(RuntimeError) as exc:
        await engine.certify(mock_certification_context)
        
    assert "Certification failed for" in str(exc.value)
