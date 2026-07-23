import pytest
from datetime import datetime, timezone
from backend.paper_execution_certification_engine.models.snapshot import (
    StageResult,
    CertificationMetadata,
    CertificationReport,
    PaperExecutionCertificationSnapshot
)
from backend.paper_execution_certification_engine.config.config import CertificationConfig

def test_models_immutability():
    stage = StageResult(stage_name="Test", passed=True, duration_ms=10.5)
    with pytest.raises(Exception): # Pydantic ValidationError for frozen=True
        stage.passed = False
        
    config = CertificationConfig()
    with pytest.raises(Exception):
        config.fail_fast = False
