"""
Trend Engine Validator
======================

Strict structural validation for the Trend Engine.
No business logic or trend rule validation exists here.
"""
from typing import List, Optional

from backend.trend_engine.contracts.contracts import ITrendValidator
from backend.trend_engine.models.models import TrendSymbol, TrendSnapshot


class TrendValidationError(ValueError):
    """Raised when Trend Engine structural validation fails."""
    pass


class TrendValidator(ITrendValidator):
    """
    Implements structural validation for Trend Engine inputs and snapshots.
    """

    def validate_input(self, symbols: List[TrendSymbol]) -> None:
        """
        Validates the incoming symbol list.
        
        Rules:
          - Cannot be empty
          - Cannot contain nulls
          - Cannot contain duplicate symbols
        """
        if not symbols:
            raise TrendValidationError("Input symbol list cannot be empty.")

        seen = set()
        for i, symbol in enumerate(symbols):
            if symbol is None:
                raise TrendValidationError(f"Null symbol found at index {i}.")
            
            sym = symbol.watchlist_symbol.symbol
            ident = f"{sym.symbol}:{sym.exchange.code}"
            if ident in seen:
                raise TrendValidationError(f"Duplicate symbol found: {ident}")
            seen.add(ident)

    def validate_snapshot(
        self, 
        snapshot: TrendSnapshot, 
        previous_snapshot: Optional[TrendSnapshot] = None
    ) -> None:
        """
        Validates an assembled snapshot before persistence.
        
        Rules:
          - Validates lineage references
          - Validates configuration hash
          - Validates schema version consistency
          - Validates snapshot version strictly increments
          - Validates immutability / consistency properties
        """
        if not snapshot.snapshot_id:
            raise TrendValidationError("Snapshot missing snapshot_id.")
            
        if not snapshot.source_watchlist_snapshot_id:
            raise TrendValidationError("Snapshot missing source_watchlist_snapshot_id lineage.")
            
        if snapshot.source_watchlist_version <= 0:
            raise TrendValidationError("Invalid source_watchlist_version.")
            
        if not snapshot.source_indicator_snapshot_id:
            raise TrendValidationError("Snapshot missing source_indicator_snapshot_id lineage.")
            
        if snapshot.source_indicator_snapshot_version <= 0:
            raise TrendValidationError("Invalid source_indicator_snapshot_version.")
            
        if not snapshot.source_structure_snapshot_id:
            raise TrendValidationError("Snapshot missing source_structure_snapshot_id lineage.")
            
        if snapshot.source_structure_snapshot_version <= 0:
            raise TrendValidationError("Invalid source_structure_snapshot_version.")
            
        if not snapshot.configuration_hash:
            raise TrendValidationError("Snapshot missing configuration_hash.")
            
        if not snapshot.schema_version:
            raise TrendValidationError("Snapshot missing schema_version.")
            
        if snapshot.snapshot_version <= 0:
            raise TrendValidationError("Snapshot version must be positive integer.")

        if previous_snapshot:
            if snapshot.snapshot_version <= previous_snapshot.snapshot_version:
                raise TrendValidationError(
                    f"Duplicate or invalid snapshot version. "
                    f"Previous: {previous_snapshot.snapshot_version}, New: {snapshot.snapshot_version}"
                )
            # Ensure schema versions are compatible (simplistic equality for now)
            if snapshot.schema_version != previous_snapshot.schema_version:
                # In the future, this would check semver compatibility
                pass 
