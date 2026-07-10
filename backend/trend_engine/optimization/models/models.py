from typing import Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import hashlib
import json

class BusinessFingerprint(BaseModel):
    """
    Deterministic hash model representing purely business-impacting inputs.
    
    MUST INCLUDE: 
    - Parent Watchlist Snapshot Version
    - Trend Config Hash
    - Trend Algorithm Version
    - Rule Versions
    - Relevant Indicator Versions
    
    MUST NEVER INCLUDE:
    - UUIDs, IDs, Timestamps
    - Runtime/Debug/Audit metadata
    - Optimization Metrics
    """
    fingerprint_version: int = Field(default=1, description="Version of the fingerprint algorithm.")
    watchlist_snapshot_version: int = Field(description="Version of the parent watchlist snapshot.")
    
    # Detection
    detection_algorithm_version: str = Field(description="Trend Detection algorithm version.")
    detection_config_hash: str = Field(description="Trend Detection configuration hash.")
    
    # Quality
    quality_algorithm_version: str = Field(description="Trend Quality algorithm version.")
    quality_config_hash: str = Field(description="Trend Quality configuration hash.")
    
    # Lifecycle
    lifecycle_algorithm_version: str = Field(description="Trend Lifecycle algorithm version.")
    lifecycle_rule_version: int = Field(description="Trend Lifecycle rule version.")
    lifecycle_config_hash: str = Field(description="Trend Lifecycle configuration hash.")
    
    # Global/Indicators
    indicator_versions: Dict[str, str] = Field(description="Versions of relevant indicators.")

    def compute_hash(self) -> str:
        """Computes a deterministic SHA-256 hash of the business inputs."""
        payload = {
            "fv": self.fingerprint_version,
            "wsv": self.watchlist_snapshot_version,
            "dav": self.detection_algorithm_version,
            "dch": self.detection_config_hash,
            "qav": self.quality_algorithm_version,
            "qch": self.quality_config_hash,
            "lav": self.lifecycle_algorithm_version,
            "lrv": self.lifecycle_rule_version,
            "lch": self.lifecycle_config_hash,
            "iv": sorted(self.indicator_versions.items())
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    model_config = {"frozen": True}

class TrendOptimizationMetrics(BaseModel):
    """Metrics for optimization execution."""
    symbols_processed_total: int = Field(default=0)
    symbols_reused_from_cache: int = Field(default=0)
    symbols_recomputed: int = Field(default=0)
    
    cache_hit_rate_percentage: float = Field(default=0.0)
    
    execution_duration_ms: float = Field(default=0.0)
    parallel_execution_time_ms: float = Field(default=0.0)

    model_config = {"frozen": True}

class TrendOptimizationSnapshot(BaseModel):
    """
    Immutable snapshot containing optimization metadata.
    
    MUST NOT duplicate business objects like TrendSnapshot.
    Instead, it references them.
    """
    snapshot_id: str = Field(description="Unique ID for this optimization snapshot.")
    snapshot_version: int = Field(default=1, description="Version of the snapshot.")
    snapshot_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # References to actual business snapshots
    trend_snapshot_id: str = Field(description="Reference to the Trend Detection Snapshot.")
    trend_quality_snapshot_id: str = Field(description="Reference to the Trend Quality Snapshot.")
    trend_lifecycle_snapshot_id: str = Field(description="Reference to the Trend Lifecycle Snapshot.")
    
    business_fingerprint: BusinessFingerprint = Field(description="The deterministic business inputs.")
    fingerprint_hash: str = Field(description="The precomputed hash of the business fingerprint.")
    
    optimization_version: str = Field(default="1.0.0", description="Version of the optimization engine.")
    configuration_hash: str = Field(description="Optimization configuration hash.")
    
    metrics: TrendOptimizationMetrics = Field(default_factory=TrendOptimizationMetrics)
    
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}

class SymbolPipelineResult(BaseModel):
    """
    Container for the fully evaluated business results for a single symbol.
    Used for caching symbol-level results in the ISymbolTrendCache.
    """
    symbol_key: str = Field(description="Format: SYMBOL:EXCHANGE")
    
    # We store dict dumps or actual business models here, but to avoid circular deps
    # or deep coupling, we can store them as raw Dicts or use Any, 
    # but since pydantic parses them, let's use Dict[str, Any] representing the raw outputs 
    # of Detection, Quality, and Lifecycle for this symbol.
    detection_result: Dict[str, Any] = Field(description="TrendDetectionSymbolResult dump")
    quality_result: Dict[str, Any] = Field(description="TrendQualitySymbolResult dump")
    lifecycle_result: Dict[str, Any] = Field(description="TrendLifecycleSymbolResult dump")

    model_config = {"frozen": True}
