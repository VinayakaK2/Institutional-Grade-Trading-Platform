from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import hashlib
from pydantic import BaseModel, Field

class LiquidityGrabQualityEnum(str, Enum):
    """
    Categorical values for the overall quality classification.
    """
    INVALID = "INVALID"
    POOR = "POOR"
    MARGINAL = "MARGINAL"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"

class MetricResult(BaseModel):
    """
    Immutable representation of a single metric's evaluation.
    Raw measurements are kept in metadata to avoid confusing the classifier.
    """
    metric_id: str = Field(description="Deterministic ID for this metric execution")
    metric_name: str = Field(description="Name of the metric")
    normalized_score: float = Field(ge=0.0, le=1.0, description="Normalized score between 0.0 and 1.0")
    metric_version: str = Field(description="Version of the metric strategy")
    execution_duration: float = Field(description="Time taken to execute in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw measurements and additional context")
    model_config = {"frozen": True}

class QualityEvidence(BaseModel):
    """
    Strongly typed evidence holding all metric results.
    Intermediate object populated before classification.
    
    Immutable -> Read-only -> Single evaluation only.
    It should never be reused across multiple pipeline executions.
    """
    support_recovery: Optional[MetricResult] = None
    recovery_strength: Optional[MetricResult] = None
    recovery_speed: Optional[MetricResult] = None
    false_break_depth: Optional[MetricResult] = None
    volume_confirmation: Optional[MetricResult] = None
    structural_consistency: Optional[MetricResult] = None
    model_config = {"frozen": True}

class ClassificationSummary(BaseModel):
    """
    The final classification of the Liquidity Grab Quality.
    """
    quality: LiquidityGrabQualityEnum = Field(description="Overall quality classification")
    classifier_algorithm_version: str = Field(description="Version of the classifier algorithm used")
    classifier_configuration_hash: str = Field(description="Hash of the configuration the classifier used")
    model_config = {"frozen": True}

class EvaluationMetadata(BaseModel):
    """Metadata surrounding the generation of the quality report."""
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when report was assembled")
    pipeline_version: str = Field(description="Pipeline version used to generate the report")
    model_config = {"frozen": True}

class LiquidityGrabQualityReport(BaseModel):
    """
    Immutable root entity representing the Quality Evaluation.
    """
    report_id: str = Field(description="Deterministic ID for this report")
    candidate_id: str = Field(description="ID of the candidate evaluated")
    symbol_id: str = Field(description="Target symbol ID")
    timeframe: str = Field(description="Target timeframe")
    
    dataset_version: int = Field(description="Dataset version used")
    parent_trend_snapshot_version: int = Field(description="Parent Trend Snapshot version")
    parent_consolidation_snapshot_version: int = Field(description="Parent Consolidation Snapshot version")
    configuration_hash: str = Field(description="Hash of the configuration used for evaluation")
    
    evidence: QualityEvidence = Field(description="The gathered metric evidence")
    classification: ClassificationSummary = Field(description="The final classification")
    metadata: EvaluationMetadata = Field(description="Evaluation metadata")

    @classmethod
    def generate_id(cls, candidate_id: str, dataset_version: int, config_hash: str, classifier_version: str) -> str:
        """
        Generates a deterministic Report ID.
        """
        payload = f"{candidate_id}_{dataset_version}_{config_hash}_{classifier_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
    model_config = {"frozen": True}
