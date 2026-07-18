import abc
from typing import Optional, List
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport

class IValidationQueryService(abc.ABC):
    """
    Read-only queries extending the basic repository operations.
    Supports complex analytics like pagination and status filtering without affecting business logic.
    """

    @abc.abstractmethod
    async def get_by_validation_id(self, validation_id: str) -> Optional[ValidationReport]:
        pass

    @abc.abstractmethod
    async def get_latest_by_symbol(self, symbol: str) -> Optional[ValidationReport]:
        pass

    @abc.abstractmethod
    async def query_by_dataset_version(self, dataset_version: int, limit: int = 100, offset: int = 0) -> List[ValidationReport]:
        pass

    @abc.abstractmethod
    async def query_by_validation_status(self, success: bool, limit: int = 100, offset: int = 0) -> List[ValidationReport]:
        pass
