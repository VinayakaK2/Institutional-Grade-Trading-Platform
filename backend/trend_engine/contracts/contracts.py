"""
Trend Engine Contracts
======================

Pure abstract interfaces for the Trend Engine.
All concrete implementations must depend on these contracts,
never on concrete classes (Dependency Inversion Principle).

These contracts define the architectural boundaries of the Trend Engine.
No business logic or implementation details exist here.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from backend.trend_engine.models.models import (
    TrendSymbol,
    TrendStageResult,
    TrendSnapshot,
)
from backend.trend_engine.pipeline.context import TrendExecutionContext
from backend.market_data.models.symbol import SymbolReference
from backend.indicator_engine.models.indicator import IndicatorResult
from backend.market_structure_engine.models.structure import MarketStructurePoint


class IIndicatorProvider(ABC):
    """
    Contract for providing Indicator data to the Trend Engine.
    Ensures Trend Engine does not directly depend on the Indicator Engine repository.
    """
    @abstractmethod
    async def get_ema_indicators(
        self, 
        symbol: SymbolReference, 
        snapshot_id: str,
        periods: List[int]
    ) -> Dict[int, IndicatorResult]:
        """
        Retrieves EMA indicators for a given symbol and snapshot.
        Returns a dictionary mapping EMA period (e.g., 20, 50, 200) to the IndicatorResult.
        """
        ...

class IStructureProvider(ABC):
    """
    Contract for providing Market Structure data to the Trend Engine.
    Ensures Trend Engine does not directly depend on the Market Structure Engine repository.
    """
    @abstractmethod
    async def get_latest_structures(
        self, 
        symbol: SymbolReference, 
        snapshot_id: str,
        limit: int = 2
    ) -> List[MarketStructurePoint]:
        """
        Retrieves the most recent market structure points for a given symbol and snapshot.
        Ordered descending by time (most recent first).
        """
        ...


class ITrendStage(ABC):
    """
    Contract for an individual stage in the Trend Pipeline.

    Each stage performs a single, focused operation on the execution context
    and returns an immutable TrendStageResult describing the outcome.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this stage."""
        ...

    @abstractmethod
    async def execute(self, context: TrendExecutionContext) -> TrendStageResult:
        """
        Executes this pipeline stage against the provided context.

        Returns:
            TrendStageResult describing the outcome.
        """
        ...


class ITrendPipeline(ABC):
    """
    Contract for the Trend Execution Pipeline.

    Manages ordered registration and sequential execution of stages.
    """

    @abstractmethod
    def register_stage(self, stage: ITrendStage) -> None:
        """Registers a stage for ordered execution."""
        ...

    @abstractmethod
    async def execute(self, context: TrendExecutionContext) -> TrendExecutionContext:
        """
        Executes all registered stages in order, mutating the context.

        Returns:
            The mutated TrendExecutionContext with accumulated results.
        """
        ...


class ITrendRepository(ABC):
    """
    Contract for persisting and retrieving trend snapshots.

    All write operations are INSERT-only. Existing snapshots must never be updated.
    """

    @abstractmethod
    async def save_snapshot(self, snapshot: TrendSnapshot) -> None:
        """Persists a new trend snapshot. INSERT-only — never UPDATE."""
        ...

    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[TrendSnapshot]:
        """Loads a snapshot by its unique ID. Returns None if not found."""
        ...

    @abstractmethod
    async def load_latest_snapshot(self) -> Optional[TrendSnapshot]:
        """Loads the most recently created snapshot. Returns None if no snapshots exist."""
        ...

    @abstractmethod
    async def load_snapshot_by_version(self, version: int) -> Optional[TrendSnapshot]:
        """Loads a snapshot by its exact version number. Returns None if not found."""
        ...

    @abstractmethod
    async def list_snapshot_history(self, limit: int = 10) -> List[TrendSnapshot]:
        """Returns the most recent snapshots, ordered by version descending."""
        ...


class ITrendValidator(ABC):
    """
    Contract for strict structural validation of Trend Engine inputs.
    """
    @abstractmethod
    def validate_input(self, symbols: List[TrendSymbol]) -> None:
        """Validates that the input symbols meet strict structural constraints."""
        ...

    @abstractmethod
    def validate_snapshot(
        self, 
        snapshot: TrendSnapshot, 
        previous_snapshot: Optional[TrendSnapshot] = None
    ) -> None:
        """Validates an assembled snapshot before persistence."""
        ...


class ITrendSnapshotBuilder(ABC):
    """
    Contract for building immutable TrendSnapshots.
    """
    @abstractmethod
    def build_snapshot(self, context: TrendExecutionContext, next_version: int) -> TrendSnapshot:
        """Constructs an immutable TrendSnapshot from a completed pipeline context."""
        ...


class ITrendEngine(ABC):
    """
    Contract for the Trend Engine Core Orchestrator.

    The Trend Engine coordinates the full execution lifecycle but delegates
    snapshot construction and persistence.
    """

    @abstractmethod
    async def generate_trend_snapshot(
        self, 
        symbols: List[TrendSymbol],
        source_watchlist_snapshot_id: str,
        source_watchlist_version: int,
        source_indicator_snapshot_id: str,
        source_indicator_snapshot_version: int,
        source_structure_snapshot_id: str,
        source_structure_snapshot_version: int,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> TrendSnapshot:
        """
        Executes the Trend Engine pipeline and returns a new immutable TrendSnapshot.
        """
        ...
