"""
Trend Quality Pipeline Context
==============================

Context propagated through the Trend Quality Pipeline stages.
"""

from typing import Dict, Any, Optional
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.models.models import TrendSnapshot

class SymbolQualityContext:
    """Mutable container for accumulating quality metrics for a single symbol."""
    def __init__(self, symbol_key: str):
        self.symbol_key = symbol_key
        self.strength_result: Optional[Any] = None
        self.consistency_result: Optional[Any] = None
        self.pullback_result: Optional[Any] = None
        self.persistence_result: Optional[Any] = None
        self.normalized_metrics: Optional[Any] = None


class QualityExecutionContext:
    """
    Mutable execution context carried through the Quality Engine pipeline.
    It provides access to the parent TrendSnapshot, the Quality Configuration,
    and manages per-symbol result accumulation.
    """
    def __init__(self, parent_snapshot: TrendSnapshot, config: TrendQualityConfig):
        self.parent_snapshot = parent_snapshot
        self.config = config
        
        # Initialize per-symbol context
        self.symbol_contexts: Dict[str, SymbolQualityContext] = {}
        for ts in parent_snapshot.symbols:
            key = f"{ts.watchlist_symbol.symbol.symbol}:{ts.watchlist_symbol.symbol.exchange.code}"
            self.symbol_contexts[key] = SymbolQualityContext(symbol_key=key)
        
        # General temporary storage for internal pipeline tracking
        self.metadata: Dict[str, Any] = {}
        self.warnings: list = []
