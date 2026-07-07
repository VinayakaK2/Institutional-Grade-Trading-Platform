from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from backend.watchlist_engine.management.models import ManagedWatchlistSnapshot, WatchlistDiff, WatchlistAuditRecord
from backend.watchlist_engine.freshness.models import FreshWatchlistSnapshot

class IManagedWatchlistRepository(ABC):
    """
    INSERT-only repository for storing ManagedWatchlistSnapshots and Audit trails.
    """
    @abstractmethod
    async def save_managed_snapshot(self, snapshot: ManagedWatchlistSnapshot, audit_record: WatchlistAuditRecord) -> None:
        pass
        
    @abstractmethod
    async def load_latest_managed_snapshot(self) -> Optional[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def load_managed_snapshot_by_version(self, version: int) -> Optional[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def get_snapshot_history(self, limit: int = 100) -> List[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def get_audit_history(self, managed_snapshot_id: str) -> List[WatchlistAuditRecord]:
        pass

class IManagedWatchlistQueryService(ABC):
    """
    Read-only query service for managing and diffing snapshots dynamically.
    """
    @abstractmethod
    async def get_latest_snapshot(self) -> Optional[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def get_snapshot_by_version(self, version: int) -> Optional[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def get_snapshot_history(self, limit: int = 100) -> List[ManagedWatchlistSnapshot]:
        pass
        
    @abstractmethod
    async def get_snapshot_diff(self, base_version: Optional[int], target_version: int) -> WatchlistDiff:
        pass
        
    @abstractmethod
    async def get_snapshot_metadata(self, version: int) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    async def get_audit_history(self, version: int) -> List[WatchlistAuditRecord]:
        pass

class IWatchlistManagementEngine(ABC):
    """
    Core engine orchestrating the promotion of FreshWatchlistSnapshots into ManagedWatchlistSnapshots.
    """
    @abstractmethod
    async def generate_managed_watchlist(self, fresh_snapshot: FreshWatchlistSnapshot) -> ManagedWatchlistSnapshot:
        pass
