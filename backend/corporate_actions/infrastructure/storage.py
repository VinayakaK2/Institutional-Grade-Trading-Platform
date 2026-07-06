from typing import List, Dict

from backend.corporate_actions.models.action import CorporateAction
from backend.corporate_actions.models.versioning import DatasetVersion, AuditLog
from backend.corporate_actions.contracts.storage import CorporateActionRepository, DatasetVersionRepository, AuditLogRepository
from backend.market_data.models.symbol import SymbolReference

class InMemoryCorporateActionRepository(CorporateActionRepository):
    def __init__(self):
        self._actions: Dict[str, CorporateAction] = {}
        
    def get_by_symbol(self, symbol: SymbolReference) -> List[CorporateAction]:
        return [a for a in self._actions.values() if a.symbol.full_name == symbol.full_name]
        
    def get_all(self) -> List[CorporateAction]:
        return list(self._actions.values())
        
    def save(self, action: CorporateAction) -> None:
        # In a real DB, this would be an upsert or insert
        self._actions[action.id] = action

class InMemoryDatasetVersionRepository(DatasetVersionRepository):
    def __init__(self):
        self._versions: Dict[str, DatasetVersion] = {}
        
    def get_by_original_version(self, original_version: str) -> List[DatasetVersion]:
        return [v for v in self._versions.values() if v.original_version == original_version]
        
    def save(self, version: DatasetVersion) -> None:
        self._versions[version.adjusted_version] = version

class InMemoryAuditLogRepository(AuditLogRepository):
    def __init__(self):
        self._logs: List[AuditLog] = []
        
    def save(self, log: AuditLog) -> None:
        self._logs.append(log)
