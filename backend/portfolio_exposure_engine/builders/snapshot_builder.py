import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.portfolio_exposure_engine.models.snapshot import PortfolioExposureSnapshot
from backend.portfolio_exposure_engine.models.exposure_models import PortfolioExposureAnalysis
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioExposureSnapshotBuilder:
    """
    Deterministic builder for PortfolioExposureSnapshot.
    """
    def __init__(self):
        self._exposure_analysis: Optional[PortfolioExposureAnalysis] = None
        self._dataset_version: Optional[str] = None
        self._parent_snapshot_references: Optional[ParentSnapshotReferences] = None
        self._configuration_hash: Optional[str] = None
        self._pipeline_version: str = "1.0"
        self._metadata: Dict[str, Any] = {}
        
    def with_exposure_analysis(self, analysis: PortfolioExposureAnalysis) -> 'PortfolioExposureSnapshotBuilder':
        self._exposure_analysis = analysis
        return self
        
    def with_dataset_version(self, version: str) -> 'PortfolioExposureSnapshotBuilder':
        self._dataset_version = version
        return self
        
    def with_parent_snapshot_references(self, refs: ParentSnapshotReferences) -> 'PortfolioExposureSnapshotBuilder':
        self._parent_snapshot_references = refs
        return self
        
    def with_configuration_hash(self, config_hash: str) -> 'PortfolioExposureSnapshotBuilder':
        self._configuration_hash = config_hash
        return self
        
    def with_pipeline_version(self, version: str) -> 'PortfolioExposureSnapshotBuilder':
        self._pipeline_version = version
        return self
        
    def with_metadata(self, metadata: Dict[str, Any]) -> 'PortfolioExposureSnapshotBuilder':
        self._metadata = metadata
        return self
        
    def build(self) -> PortfolioExposureSnapshot:
        if not self._exposure_analysis or not self._dataset_version or not self._parent_snapshot_references or not self._configuration_hash:
            raise ValueError("Exposure analysis, dataset version, parent references, and configuration hash are required.")
            
        # Canonical hash generation strictly excludes timestamps and runtime execution data.
        hash_payload = {
            "exposure_analysis": self._exposure_analysis.model_dump(),
            "lineage": self._parent_snapshot_references.model_dump()
        }
        
        # Deterministic JSON serialization
        canonical_json = json.dumps(hash_payload, sort_keys=True, separators=(',', ':'))
        snapshot_id = "port_exp_" + hashlib.sha256(canonical_json.encode()).hexdigest()
        
        return PortfolioExposureSnapshot(
            snapshot_id=snapshot_id,
            exposure_analysis=self._exposure_analysis,
            parent_snapshot_references=self._parent_snapshot_references,
            dataset_version=self._dataset_version,
            pipeline_version=self._pipeline_version,
            configuration_hash=self._configuration_hash,
            metadata=self._metadata,
            created_at=datetime.now(timezone.utc)
        )
