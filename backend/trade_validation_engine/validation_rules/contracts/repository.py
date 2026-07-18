import abc
from typing import Optional, List
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport

class IValidationReportRepository(abc.ABC):
    """
    Contract for immutable, INSERT-only persistence of ValidationReports.
    """

    @abc.abstractmethod
    async def save(self, report: ValidationReport) -> None:
        pass

    @abc.abstractmethod
    async def load(self, validation_id: str) -> Optional[ValidationReport]:
        pass

    @abc.abstractmethod
    async def exists(self, validation_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def query_by_symbol(self, symbol: str) -> List[ValidationReport]:
        pass

    @abc.abstractmethod
    async def query_by_timeframe(self, timeframe: str) -> List[ValidationReport]:
        pass

    @abc.abstractmethod
    async def query_by_dataset_version(self, dataset_version: int) -> List[ValidationReport]:
        pass

    @abc.abstractmethod
    async def query_by_parent_snapshot(self, parent_snapshot_version: str) -> List[ValidationReport]:
        pass

    @abc.abstractmethod
    async def load_latest(self, symbol: str, timeframe: str) -> Optional[ValidationReport]:
        pass
