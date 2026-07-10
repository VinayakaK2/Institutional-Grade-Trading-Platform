from pydantic import BaseModel, Field
from typing import List

class CertificationConfig(BaseModel):
    """Configuration for the Certification Engine."""
    certification_version: str = Field(default="1.0.0")
    enable_stress_testing: bool = Field(default=True)
    enable_determinism_checks: bool = Field(default=True)
    stress_dataset_sizes: List[int] = Field(default_factory=lambda: [100, 500, 1000])
    random_seed: int = Field(default=42)
    
    @property
    def config_hash(self) -> str:
        # A simple hash representation of the config
        from hashlib import sha256
        data = f"{self.certification_version}|{self.enable_stress_testing}|{self.enable_determinism_checks}|{self.stress_dataset_sizes}|{self.random_seed}"
        return sha256(data.encode('utf-8')).hexdigest()
