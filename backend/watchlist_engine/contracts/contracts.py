"""
Watchlist Engine Contracts
===========================

Pure abstract interfaces for the Watchlist Engine.
All concrete implementations must depend on these contracts,
never on concrete classes (Dependency Inversion Principle).

These contracts define the architectural boundaries of the Watchlist Engine.
No business logic or implementation details exist here.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.watchlist_engine.models.models import (
    WatchlistCandidate,
    WatchlistResult,
    WatchlistStageResult,
    WatchlistExecutionContext,
    WatchlistSnapshot,
)


class IWatchlistStage(ABC):
    """
    Contract for an individual stage in the Watchlist Pipeline.

    Each stage performs a single, focused operation on the execution context
    and returns an immutable WatchlistStageResult describing the outcome.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this stage."""
        ...

    @abstractmethod
    async def execute(self, context: WatchlistExecutionContext) -> WatchlistStageResult:
        """
        Executes this pipeline stage against the provided context.

        Returns:
            WatchlistStageResult describing the outcome.
        """
        ...


class IWatchlistPipeline(ABC):
    """
    Contract for the Watchlist Execution Pipeline.

    Manages ordered registration and sequential execution of stages.
    """

    @abstractmethod
    def register_stage(self, stage: IWatchlistStage) -> None:
        """Registers a stage for ordered execution."""
        ...

    @abstractmethod
    async def execute(self, context: WatchlistExecutionContext) -> WatchlistExecutionContext:
        """
        Executes all registered stages in order, mutating the context.

        Returns:
            The mutated WatchlistExecutionContext with accumulated results.
        """
        ...


class IWatchlistRepository(ABC):
    """
    Contract for persisting and retrieving watchlist snapshots.

    All write operations are INSERT-only. Existing snapshots must never be updated.
    """

    @abstractmethod
    async def save_snapshot(self, snapshot: WatchlistSnapshot) -> None:
        """Persists a new watchlist snapshot. INSERT-only — never UPDATE."""
        ...

    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[WatchlistSnapshot]:
        """Loads a snapshot by its unique ID. Returns None if not found."""
        ...

    @abstractmethod
    async def load_latest_snapshot(self) -> Optional[WatchlistSnapshot]:
        """Loads the most recently created snapshot. Returns None if no snapshots exist."""
        ...

    @abstractmethod
    async def load_snapshot_by_version(self, version: int) -> Optional[WatchlistSnapshot]:
        """Loads a snapshot by its exact version number. Returns None if not found."""
        ...

    @abstractmethod
    async def list_snapshot_history(self, limit: int = 10) -> List[WatchlistSnapshot]:
        """Returns the last N snapshots ordered by version descending."""
        ...


class IWatchlistValidator(ABC):
    """
    Contract for structural validation of watchlist candidates.

    Validates structural integrity only — no business rules.
    Raises WatchlistValidationError if validation fails.
    """

    @abstractmethod
    def validate(self, candidates: List[WatchlistCandidate]) -> None:
        """
        Validates the candidate list for structural correctness.

        Raises:
            WatchlistValidationError: If structural validation fails.
        """
        ...


class IWatchlistEngine(ABC):
    """
    Contract for the Watchlist Engine orchestrator.

    Coordinates the full execution lifecycle: validate → pipeline → snapshot → persist.
    """

    @abstractmethod
    async def generate_watchlist(
        self, 
        run_id: str, 
        candidates: List[WatchlistCandidate],
        source_universe_snapshot_id: Optional[str] = None,
        source_universe_version: Optional[int] = None,
        config_hash: str = "unknown",
        candidate_selection_version: Optional[str] = None
    ) -> WatchlistResult:
        """
        Executes a full watchlist generation run.

        Args:
            run_id: Unique identifier for this run — used for tracing and metadata.
            candidates: The pre-processed candidate symbols to include.

        Returns:
            WatchlistResult containing the newly created WatchlistSnapshot.
        """
        ...
