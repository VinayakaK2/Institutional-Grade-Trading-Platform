import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_state_engine.models.state import PortfolioState
from backend.portfolio_engine.models.references import ParentSnapshotReferences

class PortfolioStateSnapshotBuilder:
    """
    Deterministic builder for PortfolioStateSnapshot.
    """
    def __init__(self):
        self._portfolio_state: Optional[PortfolioState] = None
        self._dataset_version: Optional[str] = None
        self._parent_snapshot_references: Optional[ParentSnapshotReferences] = None
        self._configuration_hash: Optional[str] = None
        self._pipeline_version: str = "1.0"
        self._metadata: Dict[str, Any] = {}
        
    def with_portfolio_state(self, state: PortfolioState) -> 'PortfolioStateSnapshotBuilder':
        self._portfolio_state = state
        return self
        
    def with_dataset_version(self, version: str) -> 'PortfolioStateSnapshotBuilder':
        self._dataset_version = version
        return self
        
    def with_parent_snapshot_references(self, refs: ParentSnapshotReferences) -> 'PortfolioStateSnapshotBuilder':
        self._parent_snapshot_references = refs
        return self
        
    def with_configuration_hash(self, config_hash: str) -> 'PortfolioStateSnapshotBuilder':
        self._configuration_hash = config_hash
        return self
        
    def with_pipeline_version(self, version: str) -> 'PortfolioStateSnapshotBuilder':
        self._pipeline_version = version
        return self
        
    def with_metadata(self, metadata: Dict[str, Any]) -> 'PortfolioStateSnapshotBuilder':
        self._metadata = metadata
        return self
        
    def build(self) -> PortfolioStateSnapshot:
        if not self._portfolio_state or not self._dataset_version or not self._parent_snapshot_references or not self._configuration_hash:
            raise ValueError("Portfolio state, dataset version, parent references, and configuration hash are required.")
            
        # Canonical hash generation strictly excludes timestamps and runtime execution data.
        hash_payload = {
            "portfolio_state": self._portfolio_state.model_dump(),
            "lineage": self._parent_snapshot_references.model_dump()
        }
        
        # Deterministic JSON serialization
        canonical_json = json.dumps(hash_payload, sort_keys=True, separators=(',', ':'))
        snapshot_id = "port_state_" + hashlib.sha256(canonical_json.encode()).hexdigest()
        
        return PortfolioStateSnapshot(
            snapshot_id=snapshot_id,
            portfolio_state=self._portfolio_state,
            parent_snapshot_references=self._parent_snapshot_references,
            dataset_version=self._dataset_version,
            pipeline_version=self._pipeline_version,
            configuration_hash=self._configuration_hash,
            metadata=self._metadata,
            created_at=datetime.now(timezone.utc)
        )
