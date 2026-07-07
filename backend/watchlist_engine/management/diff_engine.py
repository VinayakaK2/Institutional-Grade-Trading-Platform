from typing import List, Optional, Dict, Any

from backend.watchlist_engine.management.models import (
    WatchlistDiff, WatchlistDiffSummary, ManagedWatchlistSnapshot
)
from backend.watchlist_engine.models.models import WatchlistSymbol

class SnapshotDiffEngine:
    """
    Deterministically computes the difference between two managed watchlist snapshots.
    
    This engine operates strictly in-memory and dynamically generates diffs.
    """
    
    def compute_diff(
        self, 
        target_snapshot: ManagedWatchlistSnapshot, 
        base_snapshot: Optional[ManagedWatchlistSnapshot] = None
    ) -> WatchlistDiff:
        """
        Computes the diff between the target_snapshot and the base_snapshot.
        If base_snapshot is None, all symbols in target_snapshot are considered 'added'.
        """
        target_candidates = target_snapshot.fresh_watchlist_snapshot.watchlist_snapshot.candidates
        target_symbols_map: Dict[str, WatchlistSymbol] = {
            f"{c.watchlist_symbol.symbol.symbol}:{c.watchlist_symbol.symbol.exchange.code}": c.watchlist_symbol
            for c in target_candidates
        }
        
        base_symbols_map: Dict[str, WatchlistSymbol] = {}
        if base_snapshot:
            base_candidates = base_snapshot.fresh_watchlist_snapshot.watchlist_snapshot.candidates
            base_symbols_map = {
                f"{c.watchlist_symbol.symbol.symbol}:{c.watchlist_symbol.symbol.exchange.code}": c.watchlist_symbol
                for c in base_candidates
            }
            
        added_symbols: List[WatchlistSymbol] = []
        removed_symbols: List[WatchlistSymbol] = []
        unchanged_symbols: List[WatchlistSymbol] = []
        
        # Sort keys to guarantee deterministic output ordering
        all_keys = sorted(list(set(target_symbols_map.keys()).union(set(base_symbols_map.keys()))))
        
        for key in all_keys:
            in_target = key in target_symbols_map
            in_base = key in base_symbols_map
            
            if in_target and not in_base:
                added_symbols.append(target_symbols_map[key])
            elif in_base and not in_target:
                removed_symbols.append(base_symbols_map[key])
            elif in_target and in_base:
                unchanged_symbols.append(target_symbols_map[key])
                
        summary = WatchlistDiffSummary(
            added_count=len(added_symbols),
            removed_count=len(removed_symbols),
            unchanged_count=len(unchanged_symbols)
        )
        
        metadata_changes: Dict[str, Any] = {}
        if base_snapshot:
            if base_snapshot.dataset_version != target_snapshot.dataset_version:
                metadata_changes["dataset_version"] = {
                    "from": base_snapshot.dataset_version,
                    "to": target_snapshot.dataset_version
                }
            if base_snapshot.pipeline_version != target_snapshot.pipeline_version:
                metadata_changes["pipeline_version"] = {
                    "from": base_snapshot.pipeline_version,
                    "to": target_snapshot.pipeline_version
                }
            if base_snapshot.config_hash != target_snapshot.config_hash:
                metadata_changes["config_hash"] = {
                    "from": base_snapshot.config_hash,
                    "to": target_snapshot.config_hash
                }
                
        return WatchlistDiff(
            base_version=base_snapshot.version if base_snapshot else None,
            target_version=target_snapshot.version,
            added_symbols=added_symbols,
            removed_symbols=removed_symbols,
            unchanged_symbols=unchanged_symbols,
            metadata_changes=metadata_changes,
            summary=summary
        )
