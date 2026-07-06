from typing import List, Protocol

from backend.corporate_actions.models.action import CorporateAction
from backend.corporate_actions.models.versioning import DatasetVersion, AuditLog
from backend.market_data.models.symbol import SymbolReference

class CorporateActionRepository(Protocol):
    def get_by_symbol(self, symbol: SymbolReference) -> List[CorporateAction]:
        ...
        
    def get_all(self) -> List[CorporateAction]:
        ...
        
    def save(self, action: CorporateAction) -> None:
        ...

class DatasetVersionRepository(Protocol):
    def get_by_original_version(self, original_version: str) -> List[DatasetVersion]:
        ...
        
    def save(self, version: DatasetVersion) -> None:
        ...

class AuditLogRepository(Protocol):
    def save(self, log: AuditLog) -> None:
        ...
