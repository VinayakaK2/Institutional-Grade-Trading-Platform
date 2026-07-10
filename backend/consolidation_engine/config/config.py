from pydantic import BaseModel, Field

class ConsolidationConfiguration(BaseModel):
    """Configuration for Consolidation Detection Pipeline.
    
    Contains strictly operational configuration.
    Business rules and thresholds are intentionally excluded.
    """
    config_version: int = Field(default=1, description="Version of this configuration format.")
    enable_parallel_execution: bool = Field(default=True, description="Whether to process symbols in parallel.")
    repository_batch_size: int = Field(default=1000, description="Batch size for saving to repository.")
    log_level: str = Field(default="INFO", description="Logging level.")

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 hash of configuration parameters."""
        payload = {
            "cv": self.config_version,
            "epe": self.enable_parallel_execution,
            "rbs": self.repository_batch_size,
            "ll": self.log_level
        }
        import json
        import hashlib
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
        
    model_config = {"frozen": True}
