from pydantic import BaseModel, Field

class PipelineConfig(BaseModel):
    fail_fast: bool = Field(default=True, description="Halt execution on first stage failure")
    max_execution_time_ms: int = Field(default=5000, description="Max allowed execution time")
    model_config = {"frozen": True}

class RepositoryConfig(BaseModel):
    batch_size: int = Field(default=100, description="Max snapshot batch size for saves")
    model_config = {"frozen": True}

class ValidationConfig(BaseModel):
    strict_mode: bool = Field(default=True, description="Require all cross-references to exist")
    model_config = {"frozen": True}

class MetadataConfig(BaseModel):
    track_durations: bool = Field(default=True, description="Track execution durations")
    model_config = {"frozen": True}

class LiquidityGrabConfiguration(BaseModel):
    version: int = Field(default=1, description="Configuration version")
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    repository: RepositoryConfig = Field(default_factory=RepositoryConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    metadata: MetadataConfig = Field(default_factory=MetadataConfig)
    
    def generate_hash(self) -> str:
        import hashlib
        dump = self.model_dump_json(exclude={"version"})
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
        
    model_config = {"frozen": True}
