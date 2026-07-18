from typing import List, Optional
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport
from backend.trade_validation_engine.validation_rules.contracts.repository import IValidationReportRepository

class PostgresValidationReportRepository(IValidationReportRepository):
    """
    PostgreSQL stub for IValidationReportRepository.
    """
    def __init__(self, connection_string: str):
        self._connection_string = connection_string

    async def save(self, report: ValidationReport) -> None:
        pass

    async def load(self, validation_id: str) -> Optional[ValidationReport]:
        return None

    async def exists(self, validation_id: str) -> bool:
        return False

    async def query_by_symbol(self, symbol: str) -> List[ValidationReport]:
        return []

    async def query_by_timeframe(self, timeframe: str) -> List[ValidationReport]:
        return []

    async def query_by_dataset_version(self, dataset_version: int) -> List[ValidationReport]:
        return []

    async def query_by_parent_snapshot(self, parent_snapshot_version: str) -> List[ValidationReport]:
        return []

    async def load_latest(self, symbol: str, timeframe: str) -> Optional[ValidationReport]:
        return None
