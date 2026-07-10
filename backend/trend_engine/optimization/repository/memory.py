from typing import Dict, Optional
import logging

from backend.trend_engine.optimization.contracts.contracts import (
    ITrendOptimizationSnapshotRepository,
    ISymbolTrendCache
)
from backend.trend_engine.optimization.models.models import (
    TrendOptimizationSnapshot,
    SymbolPipelineResult
)

logger = logging.getLogger(__name__)

class InMemoryTrendOptimizationSnapshotRepository(ITrendOptimizationSnapshotRepository):
    """
    In-memory persistence for immutable optimization snapshots.
    """
    def __init__(self) -> None:
        self._snapshots: Dict[str, TrendOptimizationSnapshot] = {}

    async def save_snapshot(self, snapshot: TrendOptimizationSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot
        logger.debug(f"Saved TrendOptimizationSnapshot: {snapshot.snapshot_id}")

    async def get_snapshot(self, snapshot_id: str) -> Optional[TrendOptimizationSnapshot]:
        return self._snapshots.get(snapshot_id)


class InMemorySymbolTrendCache(ISymbolTrendCache):
    """
    In-memory cache for reusable symbol-level optimization results.
    Keys are a composite of fingerprint_hash and symbol_key to ensure deterministic isolation.
    """
    def __init__(self) -> None:
        # composite key: "fingerprint_hash::symbol_key"
        self._cache: Dict[str, SymbolPipelineResult] = {}

    def _make_key(self, fingerprint_hash: str, symbol_key: str) -> str:
        return f"{fingerprint_hash}::{symbol_key}"

    async def get_cached_result(self, fingerprint_hash: str, symbol_key: str) -> Optional[SymbolPipelineResult]:
        key = self._make_key(fingerprint_hash, symbol_key)
        return self._cache.get(key)

    async def save_cached_result(self, fingerprint_hash: str, result: SymbolPipelineResult) -> None:
        key = self._make_key(fingerprint_hash, result.symbol_key)
        self._cache[key] = result

    async def invalidate_fingerprint(self, fingerprint_hash: str) -> None:
        """Removes all cache entries associated with a specific fingerprint hash."""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{fingerprint_hash}::")]
        for k in keys_to_delete:
            del self._cache[k]
        logger.debug(f"Invalidated {len(keys_to_delete)} cache entries for fingerprint: {fingerprint_hash}")
