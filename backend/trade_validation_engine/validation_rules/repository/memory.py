from typing import Dict, List, Optional
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport
from backend.trade_validation_engine.validation_rules.contracts.repository import IValidationReportRepository

class InMemoryValidationReportRepository(IValidationReportRepository):
    """
    In-memory stub for IValidationReportRepository.
    """
    def __init__(self):
        self._reports: Dict[str, ValidationReport] = {}

    async def save(self, report: ValidationReport) -> None:
        self._reports[report.validation_id] = report

    async def load(self, validation_id: str) -> Optional[ValidationReport]:
        return self._reports.get(validation_id)

    async def exists(self, validation_id: str) -> bool:
        return validation_id in self._reports

    async def query_by_symbol(self, symbol: str) -> List[ValidationReport]:
        return [r for r in self._reports.values() if r.symbol == symbol]

    async def query_by_timeframe(self, timeframe: str) -> List[ValidationReport]:
        return [r for r in self._reports.values() if r.timeframe == timeframe]

    async def query_by_dataset_version(self, dataset_version: int) -> List[ValidationReport]:
        return [r for r in self._reports.values() if r.dataset_version == dataset_version]

    async def query_by_parent_snapshot(self, parent_snapshot_version: str) -> List[ValidationReport]:
        # parent snapshot version corresponds to the aggregated_trade_snapshot_version in the context 
        # which is part of the ID generation, but wait, the ValidationReport doesn't explicitly store 
        # aggregated_trade_snapshot_version at root level, only validation_id. 
        # For an in-memory stub where we don't have it directly on the model, we'd mock it if needed 
        # or we could add it to ValidationReport. Let's assume it's stored in metadata for now.
        return [r for r in self._reports.values() if r.metadata.get("aggregated_trade_snapshot_version") == parent_snapshot_version]

    async def load_latest(self, symbol: str, timeframe: str) -> Optional[ValidationReport]:
        relevant = [r for r in self._reports.values() if r.symbol == symbol and r.timeframe == timeframe]
        if not relevant:
            return None
        return sorted(relevant, key=lambda r: r.created_timestamp)[-1]
