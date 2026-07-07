"""
Optimization Fingerprint
========================

Generates deterministic fingerprints for Watchlist requests to support 
incremental processing and memoization.
"""
import hashlib
import json
from typing import List

from backend.watchlist_engine.models.models import WatchlistCandidate


class OptimizationFingerprintBuilder:
    """
    Builds a deterministic Business Fingerprint for a Watchlist Execution run.
    """
    FINGERPRINT_VERSION = 1
    
    @staticmethod
    def build(
        dataset_version: str, 
        config_hash: str, 
        candidates: List[WatchlistCandidate]
    ) -> str:
        """
        Builds a fingerprint purely from business-affecting inputs.
        
        Fields included:
          - dataset_version
          - config_hash
          - Candidate Symbol IDs (sorted)
          
        Excluded:
          - Timestamps
          - Audit Metadata
          - IDs
        """
        # Sort candidate symbol strings to ensure deterministic ordering
        symbol_ids = sorted([
            f"{c.watchlist_symbol.symbol.symbol}:{c.watchlist_symbol.symbol.exchange.code}" 
            for c in candidates
        ])
        
        fingerprint_data = {
            "version": OptimizationFingerprintBuilder.FINGERPRINT_VERSION,
            "dataset_version": dataset_version,
            "config_hash": config_hash,
            "symbols": symbol_ids
        }
        
        # Serialize deterministically
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()
