from abc import ABC, abstractmethod
from typing import List, Optional, Any, Callable, Awaitable, TypeVar

from backend.trend_engine.optimization.models.models import (
    BusinessFingerprint, 
    TrendOptimizationSnapshot,
    SymbolPipelineResult
)

T_In = TypeVar('T_In')
T_Out = TypeVar('T_Out')

class ITrendOptimizationSnapshotRepository(ABC):
    """
    Persists immutable optimization snapshots.
    Does NOT store business cache.
    """
    
    @abstractmethod
    async def save_snapshot(self, snapshot: TrendOptimizationSnapshot) -> None:
        pass
        
    @abstractmethod
    async def get_snapshot(self, snapshot_id: str) -> Optional[TrendOptimizationSnapshot]:
        pass

class ISymbolTrendCache(ABC):
    """
    Stores reusable symbol-level optimization results based on the deterministic BusinessFingerprint.
    """
    
    @abstractmethod
    async def get_cached_result(self, fingerprint_hash: str, symbol_key: str) -> Optional[SymbolPipelineResult]:
        pass
        
    @abstractmethod
    async def save_cached_result(self, fingerprint_hash: str, result: SymbolPipelineResult) -> None:
        pass
        
    @abstractmethod
    async def invalidate_fingerprint(self, fingerprint_hash: str) -> None:
        pass

class IParallelExecutor(ABC):
    """
    Abstraction for executing tasks in parallel.
    Implementations must preserve original deterministic input order during merge,
    regardless of completion order.
    """
    
    @abstractmethod
    async def execute_in_parallel(self, items: List[T_In], task_func: Callable[[T_In], Awaitable[T_Out]], worker_count: int, batch_size: int) -> List[T_Out]:
        """
        Executes task_func on each item in items in parallel.
        Must return the results in the exact same order as the inputs.
        """
        pass

class ITrendOptimizationEngine(ABC):
    """
    Orchestrates the full Trend Pipeline (Detection -> Quality -> Lifecycle) 
    using optimization techniques (incremental caching, parallel execution) 
    without altering business behaviour.
    """
    
    @abstractmethod
    async def run_optimized_pipeline(
        self, 
        symbols: List[Any], # List[TrendSymbol] but avoiding strict coupling here
        business_fingerprint: BusinessFingerprint,
        source_watchlist_snapshot_id: str,
        source_watchlist_version: int,
        source_indicator_snapshot_id: str,
        source_indicator_snapshot_version: int,
        source_structure_snapshot_id: str,
        source_structure_snapshot_version: int
    ) -> TrendOptimizationSnapshot:
        """
        Executes the Trend Engine pipeline in an optimized manner.
        Returns an optimization snapshot containing references to the underlying business snapshots.
        """
        pass
