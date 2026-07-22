import json
from backend.shared.snapshots.utils import HashUtility
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.portfolio_correlation_engine.models.snapshot import PortfolioCorrelationSnapshot
from backend.portfolio_correlation_engine.models.correlation_models import PortfolioCorrelationAnalysis, CorrelationMetrics
from backend.portfolio_correlation_engine.models.references import ParentSnapshotReferences
from backend.portfolio_correlation_engine.models.configuration import PortfolioCorrelationConfigurationSnapshot

class PortfolioCorrelationSnapshotBuilder:
    """
    Deterministic builder for PortfolioCorrelationSnapshot.
    """
    def __init__(self):
        self._correlation_analysis: Optional[PortfolioCorrelationAnalysis] = None
        self._correlation_metrics: Optional[CorrelationMetrics] = None
        self._dataset_version: Optional[str] = None
        self._parent_snapshot_references: Optional[ParentSnapshotReferences] = None
        self._configuration_snapshot: Optional[PortfolioCorrelationConfigurationSnapshot] = None
        self._metadata: Dict[str, Any] = {}
        
    def with_correlation_analysis(self, analysis: PortfolioCorrelationAnalysis) -> 'PortfolioCorrelationSnapshotBuilder':
        self._correlation_analysis = analysis
        return self
        
    def with_correlation_metrics(self, metrics: CorrelationMetrics) -> 'PortfolioCorrelationSnapshotBuilder':
        self._correlation_metrics = metrics
        return self
        
    def with_dataset_version(self, version: str) -> 'PortfolioCorrelationSnapshotBuilder':
        self._dataset_version = version
        return self
        
    def with_parent_snapshot_references(self, refs: ParentSnapshotReferences) -> 'PortfolioCorrelationSnapshotBuilder':
        self._parent_snapshot_references = refs
        return self
        
    def with_configuration_snapshot(self, config_snap: PortfolioCorrelationConfigurationSnapshot) -> 'PortfolioCorrelationSnapshotBuilder':
        self._configuration_snapshot = config_snap
        return self
        
    def with_metadata(self, metadata: Dict[str, Any]) -> 'PortfolioCorrelationSnapshotBuilder':
        self._metadata = metadata
        return self
        
    def build(self) -> PortfolioCorrelationSnapshot:
        if not self._correlation_analysis or not self._correlation_metrics or not self._dataset_version or not self._parent_snapshot_references or not self._configuration_snapshot:
            raise ValueError("All fields are required to build a PortfolioCorrelationSnapshot.")
            
        # Canonical hash generation strictly excludes timestamps and runtime execution data.
        hash_payload = {
            "correlation_analysis": self._correlation_analysis.model_dump(),
            "correlation_metrics": self._correlation_metrics.model_dump(),
            "lineage": self._parent_snapshot_references.model_dump(),
            "configuration_hash": self._configuration_snapshot.configuration_hash
        }
        
        # Deterministic Hash Generation via shared utility
        snapshot_id = HashUtility.generate_id(prefix="port_corr_", payload=hash_payload)
        
        return PortfolioCorrelationSnapshot(
            snapshot_id=snapshot_id,
            schema_version="v1.0",
            correlation_analysis=self._correlation_analysis,
            correlation_metrics=self._correlation_metrics,
            parent_snapshot_references=self._parent_snapshot_references,
            configuration_snapshot_id=self._configuration_snapshot.configuration_hash,
            dataset_version=self._dataset_version,
            metadata=self._metadata,
            created_at=datetime.now(timezone.utc)
        )
