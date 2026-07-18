from pydantic import BaseModel, Field
from typing import List

class CertificationConfig(BaseModel):
    """
    Configuration for the Certification Engine.
    Fully configurable to avoid hardcoded values in testing.
    """
    # Verification Toggles
    enable_functional_verification: bool = Field(default=True, description="Enable functional verification stage")
    enable_determinism_verification: bool = Field(default=True, description="Enable determinism verification stage")
    enable_repository_verification: bool = Field(default=True, description="Enable repository verification stage")
    enable_regression_verification: bool = Field(default=True, description="Enable regression verification stage")
    enable_stress_verification: bool = Field(default=True, description="Enable stress verification stage")
    enable_performance_verification: bool = Field(default=True, description="Enable performance verification stage")
    
    # Dataset Configuration
    dataset_seed: int = Field(default=42, description="Seed for deterministic dataset generation")
    dataset_version: str = Field(default="1.0.0", description="Version of the Golden Dataset")
    dataset_size: int = Field(default=100, description="Default dataset size for functional/determinism tests")
    
    # Verification Constraints
    stress_batch_sizes: List[int] = Field(default_factory=lambda: [100, 500, 1000], description="Batch sizes for stress testing")
    performance_iterations: int = Field(default=5, description="Number of iterations for performance testing")
    allowed_memory_growth_mb: float = Field(default=10.0, description="Max acceptable progressive memory growth in MB")
    maximum_latency_threshold_ms: int = Field(default=5000, description="Max acceptable execution latency in ms")
    fail_fast: bool = Field(default=True, description="Halt certification on first failure")
    parallel_workers: int = Field(default=10, description="Concurrency limit for parallel verifications")
    
    # Internal Engine Toggles
    caching_enabled: bool = Field(default=True, description="Enable caching for the engine being tested")
    repository_validation: bool = Field(default=True, description="Validate repository insertion integrity")
    serialization_validation: bool = Field(default=True, description="Validate full round-trip serialization")
    
    # Output Configuration
    report_output_directory: str = Field(default="certification/evidence/", description="Path for persisting evidence and reports")
    timestamp_precision: str = Field(default="milliseconds", description="Precision of report timestamps")
    quality_gate_mode: str = Field(default="strict", description="Mode for quality gate checking")
    
    model_config = {"frozen": True}
