from pydantic import BaseModel, Field
from datetime import datetime, timezone

class PipelineMetadata(BaseModel):
    """
    Strongly typed infrastructure metadata for pipeline execution.
    """
    pipeline_version: str = Field(description="The pipeline version string")
    stage_count: int = Field(description="Number of stages executed in the pipeline")
    execution_mode: str = Field(default="sequential", description="Execution concurrency mode")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"frozen": True}
