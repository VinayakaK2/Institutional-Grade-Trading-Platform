from typing import List
from backend.paper_order_engine.contracts.repository import IPaperOrderRepository
from backend.paper_order_engine.models.snapshot import PaperOrderSnapshot
from backend.paper_order_engine.models.order import OrderState

class PaperOrderQueryService:
    """
    Strict CQRS read-only query service for Paper Orders.
    """
    def __init__(self, repository: IPaperOrderRepository):
        self._repository = repository

    def query_by_symbol(self, symbol: str) -> List[PaperOrderSnapshot]:
        # Typically backed by a database index; in-memory this is slow.
        raise NotImplementedError("query_by_symbol requires explicit index support.")

    def query_by_timeframe(self, timeframe: str) -> List[PaperOrderSnapshot]:
        raise NotImplementedError("query_by_timeframe requires explicit index support.")

    def query_by_parent_execution_snapshot(self, version: str) -> List[PaperOrderSnapshot]:
        raise NotImplementedError("query_by_parent_execution_snapshot requires explicit index support.")

    def query_by_order_state(self, state: OrderState) -> List[PaperOrderSnapshot]:
        raise NotImplementedError("query_by_order_state requires explicit index support.")
