from pydantic import BaseModel, ConfigDict

class CertificationConfig(BaseModel):
    """Configuration settings for the Paper Execution Certification Engine."""
    model_config = ConfigDict(frozen=True)
    
    concurrency_limit: int = 10
    fail_fast: bool = True
    
    # Stress verification configs
    stress_execution_counts: list = [100, 500, 1000]

# Fixed version string for certification fingerprinting and reporting
CERTIFICATION_VERSION = "1.0.0"
