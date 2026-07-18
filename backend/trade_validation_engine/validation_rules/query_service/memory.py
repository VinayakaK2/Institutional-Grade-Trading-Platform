from typing import List, Optional
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport
from backend.trade_validation_engine.validation_rules.contracts.query_service import IValidationQueryService
from backend.trade_validation_engine.validation_rules.repository.memory import InMemoryValidationReportRepository

class InMemoryValidationQueryService(IValidationQueryService):
    def __init__(self, repository: InMemoryValidationReportRepository):
        self._repository = repository

    async def get_by_validation_id(self, validation_id: str) -> Optional[ValidationReport]:
        return await self._repository.load(validation_id)

    async def get_latest_by_symbol(self, symbol: str) -> Optional[ValidationReport]:
        # simplified latest retrieval across all timeframes for memory stub
        reports = await self._repository.query_by_symbol(symbol)
        if not reports:
            return None
        return sorted(reports, key=lambda r: r.created_timestamp)[-1]

    async def query_by_dataset_version(self, dataset_version: int, limit: int = 100, offset: int = 0) -> List[ValidationReport]:
        reports = await self._repository.query_by_dataset_version(dataset_version)
        # Sort and paginate
        sorted_reports = sorted(reports, key=lambda r: r.created_timestamp, reverse=True)
        return sorted_reports[offset:offset+limit]

    async def query_by_validation_status(self, success: bool, limit: int = 100, offset: int = 0) -> List[ValidationReport]:
        # Filter from the underlying dict directly
        all_reports = self._repository._reports.values()
        filtered = [r for r in all_reports if r.success == success]
        sorted_reports = sorted(filtered, key=lambda r: r.created_timestamp, reverse=True)
        return sorted_reports[offset:offset+limit]
