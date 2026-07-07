from typing import Protocol, List, Any, AsyncGenerator, AsyncIterable
from backend.universe_engine.optimization.models import (
    UniverseOptimizationContext,
    OptimizedUniverse
)
from backend.universe_engine.classification.models import ClassifiedSymbol

class IUniverseOptimizationRepository(Protocol):
    """Repository contract for persisting optimized universe snapshots."""
    
    async def save_optimized_universe(self, universe: OptimizedUniverse) -> None:
        """Saves an immutable snapshot."""
        ...
        
    async def load_optimized_universe(self, optimized_universe_id: str) -> OptimizedUniverse:
        """Loads a snapshot by ID."""
        ...

from typing import Protocol, TypeVar, AsyncIterable, AsyncGenerator

T_in = TypeVar('T_in', contravariant=True)
T_out = TypeVar('T_out', covariant=True)

class IUniverseOptimizationStage(Protocol[T_in, T_out]):
    """
    Contract for optimization stages (e.g. DiffDetection, BatchBuilder, ParallelExecutor).
    """
    async def execute(self, context: UniverseOptimizationContext, items: AsyncIterable[T_in]) -> AsyncGenerator[T_out, None]:
        ...
        yield  # type: ignore
