import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.portfolio_engine.models.snapshot import PortfolioSnapshot
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioSnapshotBuilder:
    """
    Pure, deterministic builder for PortfolioSnapshot.
    """
    def __init__(self):
        self._dataset_version: Optional[str] = None
        self._parent_snapshot_references: Optional[ParentSnapshotReferences] = None
        self._configuration_hash: Optional[str] = None
        self._pipeline_version: str = "1.0"
        self._metadata: Dict[str, Any] = {}
        
    def with_dataset_version(self, version: str) -> 'PortfolioSnapshotBuilder':
        self._dataset_version = version
        return self
        
    def with_parent_snapshot_references(self, refs: ParentSnapshotReferences) -> 'PortfolioSnapshotBuilder':
        self._parent_snapshot_references = refs
        return self
        
    def with_configuration_hash(self, config_hash: str) -> 'PortfolioSnapshotBuilder':
        self._configuration_hash = config_hash
        return self
        
    def with_pipeline_version(self, version: str) -> 'PortfolioSnapshotBuilder':
        self._pipeline_version = version
        return self
        
    def with_metadata(self, metadata: Dict[str, Any]) -> 'PortfolioSnapshotBuilder':
        self._metadata = metadata
        return self
        
    def build(self) -> PortfolioSnapshot:
        if not self._dataset_version or not self._parent_snapshot_references or not self._configuration_hash:
            raise ValueError("Dataset version, parent references, and configuration hash are required.")
            
        # Canonical hash generation strictly excludes timestamps and runtime execution data.
        hash_payload = {
            "dataset_version": self._dataset_version,
            "parent_snapshot_references": self._parent_snapshot_references.model_dump(),
            "configuration_hash": self._configuration_hash,
            "pipeline_version": self._pipeline_version
        }
        
        # Deterministic JSON serialization
        canonical_json = json.dumps(hash_payload, sort_keys=True, separators=(',', ':'))
        snapshot_id = "port_" + hashlib.sha256(canonical_json.encode()).hexdigest()
        
        return PortfolioSnapshot(
            snapshot_id=snapshot_id,
            parent_snapshot_references=self._parent_snapshot_references,
            dataset_version=self._dataset_version,
            pipeline_version=self._pipeline_version,
            configuration_hash=self._configuration_hash,
            metadata=self._metadata,
            created_at=datetime.now(timezone.utc)
        )
