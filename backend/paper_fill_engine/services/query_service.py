from typing import List
from backend.paper_fill_engine.contracts.repository import IPaperFillRepository
from backend.paper_fill_engine.models.snapshot import PaperFillSnapshot
from backend.paper_fill_engine.models.fill import FillState

class PaperFillQueryService:
    """
    Strict CQRS read-only query service for Paper Fills.
    Keeps it minimal; no pagination per user instruction.
    """
    def __init__(self, repository: IPaperFillRepository):
        self._repository = repository

    def query_by_symbol(self, symbol: str) -> List[PaperFillSnapshot]:
        raise NotImplementedError("query_by_symbol requires explicit index support.")

    def query_by_timeframe(self, timeframe: str) -> List[PaperFillSnapshot]:
        raise NotImplementedError("query_by_timeframe requires explicit index support.")

    def query_by_parent_snapshot(self, version: str) -> List[PaperFillSnapshot]:
        raise NotImplementedError("query_by_parent_snapshot requires explicit index support.")

    def query_by_fill_state(self, state: FillState) -> List[PaperFillSnapshot]:
        raise NotImplementedError("query_by_fill_state requires explicit index support.")
